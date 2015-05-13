#!/usr/bin/env python
# encoding: utf-8
"""Tiny (inefficient) s3-backed static content webserver.

Use this to provide unauthenticated http access to a private S3 bucket on
your internal network, such as within a VPC. It just serves static files and
generates rudimentary index pages for "directories" in S3.

Assumes that your bucket is organized using "/" as a path separator.
"""

import io

import boto
from twitter.common import app
from twitter.common import log
from twitter.common import http
from twitter.common.exceptions import ExceptionalThread
from twitter.common.http.diagnostics import DiagnosticsEndpoints


def register_opts():
    app.add_option('--bucket', help="Bucket to serve (Required)")
    app.add_option('--prefix', default=None,
                   help=("String to prepend to all paths requested. "
                         "Use this to set a 'root directory'."))
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
        if not self.prefix:
            return rpath
        return rpath.partition(self.prefix)[-1]

    @http.route('/', method=['GET', 'HEAD'])
    def handle_root(self):
        """Handle requests for /"""
        log.info("handle_root: %s %s", self.request.method, '/')
        return self.handle_dir('/')

    @http.route('<rpath:path>/', method=['GET', 'HEAD'])
    def handle_dir(self, rpath):
        """Handle requests for directories."""
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
        """Handle requests for paths that could be files or directories."""
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


def proxy_main():
    """Proxy main function.

    setuptools entrypoints with twitter.common.app is so awkward.
    """
    def main(_, opts):
        """Main"""

        if not opts.bucket:
            log.error('--bucket is required.')
            app.help()

        server = S3Web(bucket=opts.bucket,
                       prefix=opts.prefix,
                       access_key_id=opts.access_key_id,
                       secret_key=opts.secret_key)
        thread = ExceptionalThread(
            target=lambda: server.run(opts.listen,
                                      opts.port,
                                      server='cherrypy'))
        thread.daemon = True
        thread.start()

        log.info('Ready.')
        app.wait_forever()

    register_opts()
    app.set_usage(__doc__)
    app.set_option('twitter_common_log_stderr_log_level', 'google:INFO')
    app.set_name('s3webfront')
    app.main()


if __name__ == '__main__':
    proxy_main()
