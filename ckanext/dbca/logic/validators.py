import ckan.plugins.toolkit as tk
import logging
import datetime
import pytz


log = logging.getLogger(__name__)


def dbca_required(value):
    if not value or value is tk.missing:
        raise tk.Invalid(tk._("Required"))
    return value


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
    local_now = utc_now.astimezone(aus_tz)

    # Embargo date is assumed to be Perth from the web form so we are adding Perth timezone
    local_embargo_date = aus_tz.localize(embargo_date)

    if local_embargo_date < local_now:
        raise tk.Invalid(
            tk._(f'The embargo date selected must be in the future')
        )

     # Convert the date to UTC to be saved in database
    utc_embargo_date = embargo_date.astimezone(pytz.utc)
    utc_embargo_date = utc_embargo_date.replace(tzinfo=None).isoformat()
    log.debug(f"Converted Embargo date to UTC {utc_embargo_date}")
    return utc_embargo_date


def dbca_embargo_date_package_visibility(key, data, errors, context):
    if data.get(('private',)) == 'False' and data.get(('embargo',)):
        errors[key].append(tk._(f"The status of the dataset must be Private"))


def get_validators():
    return {
        "dbca_required": dbca_required,
        "dbca_embargo_date_validator": dbca_embargo_date_validator,
        "dbca_embargo_date_package_visibility": dbca_embargo_date_package_visibility,
    }
