import json
from types import SimpleNamespace

import ckanext.dbca.logic.action as action


def test_dbca_get_geospatial_coverage_formats_spatial_matches(monkeypatch):
    geometry = {
        "type": "Polygon",
        "coordinates": [[[115.8, -31.9], [115.9, -31.9], [115.9, -32.0], [115.8, -31.9]]],
    }
    matches = [
        SimpleNamespace(label="Perth Metro", geometry=geometry),
    ]

    monkeypatch.setattr(
        action.dbca_model.DbcaSpatial,
        "get_like_label",
        lambda q, limit: matches,
    )

    results = action.dbca_get_geospatial_coverage({}, {"q": "per", "limit": "5"})

    assert results == [
        {
            "name": "Perth Metro",
            "value": json.dumps(geometry),
        }
    ]


def test_dbca_get_geospatial_coverage_returns_empty_list_without_query():
    assert action.dbca_get_geospatial_coverage({}, {"q": ""}) == []
