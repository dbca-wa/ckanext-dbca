from flask import Blueprint


dbca = Blueprint(
    "dbca", __name__)


def page():
    return "Hello, DBCA! This is a custom URL from the extension ckanext-dbca."


dbca.add_url_rule(
    "/dbca/page", view_func=page)


def get_blueprints():
    return [dbca]
