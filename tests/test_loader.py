#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import numbers
import image_loader.loader as aut
from functools import partial


#def test_load():
#    assert load(1) == 1
#    assert load(2) == 1
#    assert load(7) == 13
#    with pytest.raises(AssertionError):
#        load(-10)

def test_pipeline():
    evenf = partial(filter, lambda x: x%2==0)
    assert 6 == aut.pipeline(range(5), list, evenf, sum)
    assert 0 == aut.pipeline([], list, evenf, sum)
    assert [1,2] == aut.pipeline([1,2])
    with pytest.raises(TypeError):
        assert 0 == aut.pipeline(None, list, evenf, sum)


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
