==========
S3WebFront
==========

S3WebFront is a tiny webserver intended to provide unauthenticated http access
to files in private S3 buckets.  This is useful if you have data in S3 that is
necessary for bootstrapping apps within your private/internal network or VPC,
but are unable to use IP-based whitelists or use normal authenticated methods
of talking to S3.

This is not meant to be a general purpose web server; it is rather inefficient
in that it retrieves the entire object requested from S3 and stores it in RAM
prior to serving it to the requesting client.  It has no intelligence around
index pages, redirects, rewrites, or anything like that.  It **is** suitable
for things like git clones, though!

Simple usage:

.. code:: sh

    python setup.py install
    s3webfront --bucket your-private-bucket \
               --prefix optional/subdir \
               --port 8080

Now any http GET requests to localhost:8080 will be proxied and served
relative to s3://your-private-bucket/optional/subdir. Easy as cake.
