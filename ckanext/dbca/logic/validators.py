import ckan.plugins.toolkit as tk
import geojson
import logging
import datetime
import pytz


log = logging.getLogger(__name__)


def dbca_embargo_date_validator(embargo_date):
    '''Validate Embargo Date for Australia/Perth timezone'''
    if not embargo_date:
        return
    if tk.get_endpoint() == ('dataset_resource', 'new') or tk.get_endpoint() == ('dataset_resource', 'edit'):
        return embargo_date

    log.debug(f"Embargo date received to {embargo_date}")

    # UTC now converted to Perth timezone
    aus_tz = tk.h.get_display_timezone()
    utc_now = pytz.utc.localize(datetime.datetime.utcnow())
    local_now = utc_now.astimezone(aus_tz).date()

    # Embargo date is assumed to be Perth from the web form so we are adding Perth timezone
    local_embargo_date = aus_tz.localize(embargo_date).date()

    if local_embargo_date < local_now:
        raise tk.Invalid(
            tk._('The embargo date selected must be in the future')
        )

    return local_embargo_date


def dbca_embargo_date_package_visibility(key, data, errors, context):
    if data.get(('private',)) == 'False' and data.get(('embargo',)):
        errors[key].append(tk._("Only private datasets can be embargoed"))


def dbca_validate_geojson(value):
    """
    Validate the format of GeoJSON.
    """
    if len(value) > 0:
        try:
            # Load JSON string to geojson object.
            geojson_obj = geojson.loads(value)
        except Exception:
            raise tk.Invalid('Not a valid JSON string.')

        if geojson_obj.__class__.__name__ != 'Polygon':
            raise tk.Invalid('GeoJSON Polygon is needed.')

    return value


def dbca_resource_size(key, data, errors, context):
    # The new validator checks to see if the resource is an upload
    url_type_key = key[0:2] + ('url_type',)
    resource_upload = data.get(url_type_key) == 'upload'
    if not resource_upload:
        return

    # TODO: Get the logged in user and the datasets (package) organisation ID from the context
    # TODO: Check what role the user has for this organisation

    resource_size = data.get(key)
    # TODO: Get the CKAN config value for the resource upload limit for the user's role (convert the config value from MB to bytes)
    resource_size_limit = tk.config.get('ckan.max_resource_size')
    # Validate that the resource size is not over the limit
    if resource_size > resource_size_limit:
        # Raise an Invalid exception with message 'File upload too large'
        raise tk.Invalid('File upload too large')
    

def get_validators():
    return {
        "dbca_embargo_date_validator": dbca_embargo_date_validator,
        "dbca_embargo_date_package_visibility": dbca_embargo_date_package_visibility,
        "dbca_validate_geojson": dbca_validate_geojson,
        "dbca_resource_size": dbca_resource_size
    }
