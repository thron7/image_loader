#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
  loader -- a tool to load images from the internet
"""
from __future__ import division, print_function, absolute_import

import argparse
import sys
import logging
import os
import errno
import fcntl
import time
import shutil
from functools import reduce
from concurrent.futures import ThreadPoolExecutor

from pymaybe import maybe
import urllib3

from image_loader import __version__

# - runtime params -------------------------------------------------------------
RequestTimeoutSecs = 10
MaxNumPools = 10 # this is the default; increase this with very heterogenous urls in the input, to trade space for speed
MaxThreads = 10
MaxHTTPConnections = MaxThreads # having more threads than connections in a pool might result in (harmless) warnings
# - params end -----------------------------------------------------------------

_logger = logging.getLogger(__name__)


def pipeline(seed, *funcs):
    """Compose functions where the return value of one is the argument
       to the next, starting with the <seed> data."""
    return reduce(lambda accu,func: func(accu), funcs, seed)


def is_real_string(s):
    "Check if s is a string with some contents"
    return isinstance(s, str) and bool(s.strip())


def file_mtime(outfile):
    "Return the mtime epoc secs for a local path"
    if not os.path.exists(outfile):
        return 0  # fake mtime, everything should be younger than that
    else:
        return os.stat(outfile).st_mtime


def format_date(epocsecs):
    """Format epoc secs to a time string suitable for If-Modified-Since request header
       Example: 'Wed, 21 Oct 2015 07:28:00 GMT'"""
    t = time.gmtime(epocsecs)
    # rolling own, as time.strftime is in part locale-dependent (e.g. '%a' for short weekday)
    s = "Mon Tue Wed Thu Fri Sat Sun".split()[t.tm_wday] + ", "
    s += "%02d " % (t.tm_mday,)
    s += "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()[t.tm_mon - 1] + " "
    s += "%d %02d:%02d:%02d GMT" % (t.tm_year, t.tm_hour, t.tm_min, t.tm_sec)
    return s


def get_out_file(url, outdir):
    "Construct output file path from url"
    return os.path.join(outdir, os.path.basename(url))


def process_incoming(response, outdir):
    "Process data from web request"
    if not maybe(response.info().get('Content-Type')).or_else("").startswith('image/'):
        _logger.error("Apparently not an image file, skipping: {}".format(response.geturl()))
    else:
        file_name = get_out_file(response.geturl(), outdir)
        with open(file_name, 'wb') as out_file:
            # try locking the out_file, to allow for overlapping runs of the script
            # or a local Web server opening the file for reading (provided it uses locking too)
            try:
                fcntl.lockf(out_file, fcntl.LOCK_EX | fcntl.LOCK_NB)  # POSIX locking should be enough for Debian deployments
            except OSError as e:
                if e.errno in (errno.EACCESS, errno.EAGAIN):
                    _logger.error("Cannot obtain lock for localfile, skipping: {}".format(file_name))
                else:
                    raise
            else:
                _logger.info("Downloading image: {}".format(response.geturl()))
                shutil.copyfileobj(response, out_file) # let exceptions like OSError propagate


def download_url(pool, url, outdir, force):
    "Make the web request"
    url = url.strip()
    if not is_real_string(url):
        return
    else:
        headers = {}
        if not force:
            headers.update({'If-Modified-Since' : pipeline(get_out_file(url, outdir)
                                                           , file_mtime
                                                           , format_date)
                          })
        response = pool.request('GET'
                        , url
                        , timeout = RequestTimeoutSecs
                        , preload_content = False
                        , headers = headers
                    )
        # TODO: 
        # - fork out multiple threads, to load images in parallel?
        # - slow down requests to the same server, so not to overrun it with requests
        if response and response.status == 200:
            process_incoming(response, outdir)
        elif response and response.status == 304:
            _logger.info("Local copy of url is fresh: {}".format(url))
        else:
            _logger.error("Unable to download url: {} - error: {} - {}".format(
                url, response.status, response.msg))
        response.release_conn()


def get_url_iter(fpath):
    "Open the file with the urls"
    assert is_real_string(fpath), "Empty file path: {}".format(fpath)
    return open(fpath, 'r')


def assert_destdir(dirpath):
    "Make sure we can use the output directory"
    if not os.path.exists(dirpath):
        _logger.info("Creating output directory: {}".format(dirpath))
        os.makedirs(dirpath, mode=0o750)
    else:
        assert os.path.isdir(dirpath) and os.access(dirpath, os.W_OK|os.X_OK), \
               "Output dir is either not a directory or not writeable: {}".format(dirpath)


def load(urlfile, destdir, force):
    "Download images with URLs from file into destdir"
    assert_destdir(destdir)
    connection_pool = urllib3.PoolManager(maxsize=MaxHTTPConnections, num_pools=MaxNumPools)
    thread_pool = ThreadPoolExecutor(MaxThreads)
    with get_url_iter(urlfile) as urls:
        for url in urls:
            thread_pool.submit(download_url, connection_pool, url, destdir, force)


def parse_args(args):
    """Parse command line parameters

    Args:
      args ([str]): command line parameters as list of strings

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = argparse.ArgumentParser(
        description="Download images listed in a file")
    parser.add_argument(
        '--version',
        action='version',
        version='image_loader {ver}'.format(ver=__version__))
    parser.add_argument(
        dest="fpath",
        help="file path with image URLs, one per line",
        type=str,
        metavar="URLFILE")
    parser.add_argument(
        #'-o',
        #'--outdir',
        dest="outdir",
        help="local output directory",
        type=str,
        metavar="DIRECTORY")
    parser.add_argument(
        '-f',
        '--force',
        dest="force",
        help="force download even if local cache is up-to-date (default; false)",
        action='store_true',
    )
    parser.add_argument(
        '-v',
        '--verbose',
        dest="loglevel",
        help="set loglevel to INFO",
        action='store_const',
        const=logging.INFO)
    parser.add_argument(
        '-vv',
        '--very-verbose',
        dest="loglevel",
        help="set loglevel to DEBUG",
        action='store_const',
        const=logging.DEBUG)
    return parser.parse_args(args)


def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(level=loglevel, stream=sys.stdout,
                        format=logformat, datefmt="%Y-%m-%d %H:%M:%S")


def main(args):
    """Main entry point allowing external calls

    Args:
      args ([str]): command line parameter list
    """
    args = parse_args(args)
    setup_logging(args.loglevel)
    _logger.debug("Starting downloading images...")
    load(args.fpath, args.outdir, args.force)


def run():
    """Entry point for console_scripts
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
