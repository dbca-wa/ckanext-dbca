"""Tests for validators.py."""

import pytest

import ckan.plugins.toolkit as tk

from ckanext.dbca.logic import validators


def test_dbca_reauired_with_valid_value():
    assert validators.dbca_required("value") == "value"


def test_dbca_reauired_with_invalid_value():
    with pytest.raises(tk.Invalid):
        validators.dbca_required(None)
