#!/usr/bin/env python
# encoding: utf-8
"""Tiny inefficient s3-backed webserver"""

import io
import time

import boto
from twitter.common import app
from twitter.common import log
from twitter.common import http
from twitter.common.exceptions import ExceptionalThread
from twitter.common.http.diagnostics import DiagnosticsEndpoints

app.add_option('--bucket', default='folsom-labs-artifacts')
app.add_option('--prefix', default=None)
app.add_option('--access-key-id', default=None)
app.add_option('--secret-key', default=None)
app.add_option('--port', help='http port', default=8080)
app.add_option('--listen',
               help='IP address to listen for http connections.',
               default='0.0.0.0')


class S3Web(http.HttpServer, DiagnosticsEndpoints):
    def __init__(self, bucket=None, prefix=None,
                 access_key_id=None, secret_key=None):
        self.s3con = boto.connect_s3(access_key_id, secret_key)
        self.bucket = self.s3con.get_bucket(bucket)
        self.prefix = prefix or ''

        DiagnosticsEndpoints.__init__(self)
        http.HttpServer.__init__(self)

    def _fixpath(self, rpath):
        """Trim the chroot prefix from a path."""
        return rpath.partition(self.prefix)[-1]

    @http.route('/', method=['GET','HEAD'])
    def handle_root(self):
        log.info("handle_root: %s %s", self.request.method, '/')
        return self.handle_dir('/')

    @http.route('<rpath:path>/', method=['GET','HEAD'])
    def handle_dir(self, rpath):
        rpath = rpath.lstrip('/')
        if rpath:
            log.info("handle_dir: %s %s", self.request.method, rpath)
            olist = list(self.bucket.list(self.prefix + rpath + '/',
                                          delimiter='/'))
        else:
            olist = list(self.bucket.list(self.prefix + '', delimiter='/'))
        if not olist:
            return self.abort(404, 'That is not a thing :(')

        output = io.StringIO()
        output.write(u'<ul>\n')
        for item in olist:
            name = self._fixpath(item.name)
            output.write(
                u'<li><a href="/{name}">{name}</a>\n'.format(name=name))
        output.write(u'</ul>')
        output.seek(0)
        return output

    @http.route('/<rpath:path>', method=['GET', 'HEAD'])
    def handle_path(self, rpath):
        log.info("handle_path: %s %s", self.request.method, rpath)
        key = self.bucket.get_key(self.prefix + rpath)
        if key:
            fp = io.BytesIO()
            key.get_file(fp)
            fp.seek(0)
            self.response.set_header('Content-type',
                                     key.content_type)
            return fp

        # Not a key. Maybe a prefix?
        return self.handle_dir(rpath)


def main(_, opts):
    """Main"""

    server = S3Web(bucket=opts.bucket,
                   prefix=opts.prefix,
                   access_key_id=opts.access_key_id,
                   secret_key=opts.secret_key)
    thread = ExceptionalThread(target=lambda: server.run(opts.listen,
                                                         opts.port,
                                                         server='cherrypy'))
    thread.daemon = True
    thread.start()

    # Wait forever, basically.
    while True:
        time.sleep(100)


if __name__ == '__main__':
    app.main()
