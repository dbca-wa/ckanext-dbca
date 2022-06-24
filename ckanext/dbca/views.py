from flask import Blueprint


dbca = Blueprint(
    "dbca", __name__)


def page():
    return "Hello, dbca!"


dbca.add_url_rule(
    "/dbca/page", view_func=page)


def get_blueprints():
    return [dbca]
