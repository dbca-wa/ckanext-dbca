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


def test_parse_embargo_date_accepts_both_stored_formats():
    expected = action.datetime.date(2026, 9, 4)

    assert action._parse_embargo_date("2026-09-04") == expected
    assert action._parse_embargo_date("2026-09-04 00:00:00") == expected


def test_parse_embargo_date_returns_none_for_unusable_values():
    for value in (None, "", "not-a-date", "04/09/2026"):
        assert action._parse_embargo_date(value) is None


def test_dbca_get_packages_to_be_published_or_notified_skips_unreadable_dates(monkeypatch):
    """One bad extra must not stop the other datasets being published."""
    aus_tz = action.pytz.timezone("Australia/Perth")
    today = action.datetime.datetime.now(aus_tz).date()

    due = SimpleNamespace(name="due-today")
    due_extra = SimpleNamespace(value=today.strftime("%Y-%m-%d"))
    broken = SimpleNamespace(name="broken-date")
    broken_extra = SimpleNamespace(value="not-a-date")
    upcoming = SimpleNamespace(name="due-in-7-days")
    upcoming_extra = SimpleNamespace(
        value=(today + action.datetime.timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
    )

    query = SimpleNamespace()
    query.join = lambda *args, **kwargs: query
    query.filter = lambda *args, **kwargs: query
    query.all = lambda: [
        (due, due_extra),
        (broken, broken_extra),
        (upcoming, upcoming_extra),
    ]

    monkeypatch.setattr(action.tk.h, "get_display_timezone", lambda: aus_tz, raising=False)
    monkeypatch.setattr(action.model.Session, "query", lambda *args: query)

    results = action.dbca_get_packages_to_be_published_or_notified({}, {})

    assert results["to_publish"] == [(due, due_extra)]
    assert results["to_notify"] == [(upcoming, upcoming_extra)]
