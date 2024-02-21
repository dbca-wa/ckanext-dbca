from flask import Blueprint
from ckan.views import api as ckan_api
from ckan.plugins import toolkit

dbca = Blueprint(
    "dbca", __name__)


def spatial_autocomplete():
    q = toolkit.request.args.get('incomplete', '')
    limit = toolkit.request.args.get('limit')
    geospatial_coverages = []
    if q:
        data_dict = {'q': q, 'limit': limit}
        geospatial_coverages = toolkit.get_action(u'dbca_get_geospatial_coverage')({}, data_dict)

    result_set = {'ResultSet': {'Result': geospatial_coverages}}
    return ckan_api._finish_ok(result_set)


dbca.add_url_rule(
    "/dbca/spatial_autocomplete", view_func=spatial_autocomplete)


def get_blueprints():
    return [dbca]
