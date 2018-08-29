#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from image_loader.loader import load

__author__ = "thron7"
__copyright__ = "thron7"
__license__ = "mit"


def test_load():
    assert load(1) == 1
    assert load(2) == 1
    assert load(7) == 13
    with pytest.raises(AssertionError):
        load(-10)
