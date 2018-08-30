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

import urllib.request
import shutil

from image_loader import __version__

__author__ = "thron7"
__copyright__ = "thron7"
__license__ = "mit"

_logger = logging.getLogger(__name__)


def is_real_string(s):
    """Check if s is a string with contents"""
    return s and s.strip()


def download_url(url, outdir):
    url = url.strip()
    if not is_real_string(url):
        return
    file_name = os.path.join(outdir, os.path.basename(url))
    with urllib.request.urlopen(url) as response, open(file_name, 'wb') as out_file:
        if response and response.code == 200:
            _logger.info("Downloading image: {}".format(url))
            # TODO: check contents-type of response, e.g. image/png etc.?
            # TODO: control the mode of the target file?
            # TODO: catch exception of copyfileobj?
            # TODO: try HEAD for existing files?
            # TODO: control timing, so we don't overrun the 5min interval?
            # TODO: fork out multiple "threads", to load images in parallel?
            shutil.copyfileobj(response, out_file)
        else:
            _logger.error("Unable to download url: {} - error: {} - {}".format(
                url, response.code, response.msg))


def get_url_iter(fpath):
    assert is_real_string(fpath), "Empty file path: {}".format(fpath)
    return open(fpath, 'r')


def assert_destdir(dirpath):
    if not os.path.exists(dirpath):
        os.makedirs(dirpath, mode=0o750)
    else:
        assert os.path.isdir(dirpath) and os.access(dirpath, os.W_OK|os.X_OK), \
               "Output dir is either not a directory or not writeable: {}".format(dirpath)


def load(urlfile, destdir):
    """Download images with URLs from file into destdir"""
    assert_destdir(destdir)
    with get_url_iter(urlfile) as urls:
        for url in urls:
            download_url(url, destdir)


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
    #print("The {}-th Fibonacci number is {}".format(args.n, fib(args.n)))
    load(args.fpath, args.outdir)
    _logger.info("Script ends here")


def run():
    """Entry point for console_scripts
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
