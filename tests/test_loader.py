#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import numbers
import io
import os
import stat
import image_loader.loader as aut
from functools import partial
import urllib3
from pymaybe import maybe


def test_pipeline():
    evenf = partial(filter, lambda x: x%2==0)
    assert 6 == aut.pipeline(range(5), list, evenf, sum)
    assert 0 == aut.pipeline([], list, evenf, sum)
    assert [1,2] == aut.pipeline([1,2])
    with pytest.raises(TypeError):
        aut.pipeline(None, list, evenf, sum)


def test_is_real_string():
    assert True == aut.is_real_string("foo")
    assert True == aut.is_real_string("  t  ")
    assert False == aut.is_real_string("")
    assert False == aut.is_real_string("   ")
    assert False == aut.is_real_string(None)
    assert False == aut.is_real_string(3)


def test_file_mtime():
    result = aut.file_mtime("README.rst")
    assert isinstance(result, numbers.Number) and result > 0
    result = aut.file_mtime("__THIS_DOES_NOT_EXIST!!!__")
    assert isinstance(result, numbers.Number) and result == 0


def test_format_date():
    epocs = 1536150095.59747
    fstring = 'Wed, 05 Sep 2018 12:21:35 GMT'
    assert fstring == aut.format_date(epocs)


def test_get_out_file():
    url = 'http://some.server.net/imgs/foo.png'
    outdir = '/usr/local/www/img'
    outfile = '/usr/local/www/img/foo.png'
    assert outfile == aut.get_out_file(url, outdir)
    assert outdir + '/' == aut.get_out_file('', outdir)
    assert 'foo.png' == aut.get_out_file(url, '')

#import functools
#def test_partial(monkeypatch):
#    with monkeypatch.context() as m:
#        m.setattr(functools, "partial", 3)
#        assert functools.partial == 3

def test_get_url_iter():
    result = aut.get_url_iter("README.rst")
    assert isinstance(result, io.IOBase)
    with pytest.raises(AssertionError):
        aut.get_url_iter("")
    with pytest.raises(FileNotFoundError):
        aut.get_url_iter("__THIS_DOES_NOT_EXIST!!!__")


def test_assert_destdir(tmpdir):
    with pytest.raises(AssertionError):
        aut.assert_destdir("README.rst")
    tmppath = os.path.join(tmpdir, "foo", "bar")
    aut.assert_destdir(tmppath)
    assert os.path.exists(tmppath)
    mode = os.stat(tmppath)
    assert stat.S_ISDIR(mode.st_mode) and stat.S_IMODE(mode.st_mode) == 0o750
    os.rmdir(tmppath)


def fake_request(*args, **kwargs):
    response = urllib3.response.HTTPResponse()
    print(kwargs)
    mod_since = maybe(kwargs)['headers']['If-Modified-Since']
    if mod_since.is_some():
        response.status = 304  # pretend nothing has changed
    else:
        response.status = 200
        data = open("README.rst", "r").read()
        response.body = data
    response.headers.update({'Content-Type':'image/jpg'})
    return response


def get_mtime(localpath):
    if not os.path.exists(localpath):
        return -1
    else:
        return os.stat(localpath).st_mode


def test_download_url(tmpdir, monkeypatch):
    pool = urllib3.PoolManager()
    url = "foo.jpg"
    outdir = os.path.join(tmpdir, "imgs")
    localpath = os.path.join(outdir, url)
    with monkeypatch.context() as m:
        m.setattr(urllib3.PoolManager, "request", fake_request)
        aut.download_url(pool, url, outdir, False)
        print(localpath)
        t1 = get_mtime(localpath)
        assert t1 > 0
        aut.download_url(pool, url, outdir, True)
        t2 = get_mtime(localpath)
        assert t2 > t1
