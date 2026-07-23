import json

from flask import Flask

import ckanext.dbca.views as views


def test_spatial_autocomplete_calls_action_with_query_and_limit(monkeypatch):
    app = Flask(__name__)
    app.register_blueprint(views.dbca)
    action_calls = []
    action_results = [{"name": "Perth Metro", "value": '{"type": "Polygon"}'}]

    def fake_get_action(action_name):
        assert action_name == "dbca_get_geospatial_coverage"

        def fake_action(context, data_dict):
            action_calls.append((context, data_dict))
            return action_results

        return fake_action

    monkeypatch.setattr(views.toolkit, "get_action", fake_get_action)

    response = app.test_client().get(
        "/dbca/spatial_autocomplete?incomplete=per&limit=5"
    )

    assert response.status_code == 200
    assert json.loads(response.data) == {"ResultSet": {"Result": action_results}}
    assert action_calls == [({}, {"q": "per", "limit": "5"})]


def test_spatial_autocomplete_does_not_call_action_without_query(monkeypatch):
    app = Flask(__name__)
    app.register_blueprint(views.dbca)
    action_called = False

    def fake_get_action(action_name):
        nonlocal action_called
        action_called = True

    monkeypatch.setattr(views.toolkit, "get_action", fake_get_action)

    response = app.test_client().get("/dbca/spatial_autocomplete")

    assert response.status_code == 200
    assert json.loads(response.data) == {"ResultSet": {"Result": []}}
    assert action_called is False
