"""Tests for helpers.py."""

import ckanext.dbca.helpers as helpers


def test_dbca_hello():
    assert helpers.dbca_hello() == "Hello, dbca!"
