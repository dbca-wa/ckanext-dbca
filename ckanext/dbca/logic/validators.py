import ckan.plugins.toolkit as tk
import ckan.authz as authz
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

    # Get the max resource size from the CKAN config
    sysadmin_resource_upload_limit = int(tk.config.get('ckanext.dbca.sysadmin_resource_upload_limit'))
    org_admin_resource_upload_limit = int(tk.config.get('ckanext.dbca.org_admin_resource_upload_limit'))
    org_editor_resource_upload_limit = int(tk.config.get('ckanext.dbca.org_editor_resource_upload_limit'))

    # Convert the max resource size from MB to bytes
    sysadmin_resource_upload_limit_bytes = sysadmin_resource_upload_limit * 1024 * 1024
    org_admin_resource_upload_limit_bytes = org_admin_resource_upload_limit * 1024 * 1024
    org_editor_resource_upload_limit_bytes = org_editor_resource_upload_limit * 1024 * 1024

    # Get the resource size from the data
    resource_size = data.get(key)

    # Get the logged in user.
    user = context.get('user')
    is_sysadmin = authz.is_sysadmin(user)

    # If the user is sysadmin, allow them to upload up to the sysadmin limit.
    if is_sysadmin:
        if resource_size <= sysadmin_resource_upload_limit_bytes:
            return
        else:
            raise tk.Invalid('File upload too large')

    # Get the organization ID from the data
    org_id = data.get(('owner_org',))

    # Get the user's role in the organization
    user_role = authz.users_role_for_group_or_org(org_id, user)

    # If the user is not a member of the organization, raise an error.
    if user_role is None:
        raise tk.Invalid('User is not a member of the organization')

    # If the user is an admin, allow them to upload up to the org admin limit.
    if user_role == 'admin':
        if resource_size <= org_admin_resource_upload_limit_bytes:
            return
        else:
            raise tk.Invalid('File upload too large')

    # If the user is an editor, allow them to upload up to the org editor limit.
    if user_role == 'editor':
        if resource_size <= org_editor_resource_upload_limit_bytes:
            return
        else:
            raise tk.Invalid('File upload too large')


def get_validators():
    return {
        "dbca_embargo_date_validator": dbca_embargo_date_validator,
        "dbca_embargo_date_package_visibility": dbca_embargo_date_package_visibility,
        "dbca_validate_geojson": dbca_validate_geojson,
        "dbca_resource_size": dbca_resource_size
    }
