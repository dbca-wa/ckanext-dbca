import datetime
import logging
import pytz
import json

import ckan.model as model
import ckan.plugins.toolkit as tk
import ckan.logic as logic
import ckanext.dbca.model as dbca_model

log = logging.getLogger(__name__)


def _parse_embargo_date(value):
    '''
    Parse an embargo package_extra value, or return None if it is unusable.
    Historic rows were written with a time component, so accept both formats.
    '''
    if not value:
        return None
    try:
        return datetime.datetime.strptime(value[:10], '%Y-%m-%d').date()
    except (TypeError, ValueError):
        return None


@tk.side_effect_free
def dbca_get_packages_to_be_published_or_notified(context, data_dict):
    '''
    Get all packages that need to be published or need to be notified.
    Notification will be sent for package that will be published in the next 7 days.
    '''
    # UTC now converted to Perth timezone
    aus_tz = tk.h.get_display_timezone()
    utc_now = pytz.utc.localize(datetime.datetime.utcnow())
    local_now = utc_now.astimezone(aus_tz).date()

    # Calculate the date 7 days from now
    date_in_7_days = local_now + datetime.timedelta(days=7)

    # Query all active private packages with an embargo date
    packages = model.Session.query(model.Package, model.PackageExtra) \
        .join(model.PackageExtra, model.Package.id == model.PackageExtra.package_id) \
        .filter(model.PackageExtra.key == 'embargo') \
        .filter(model.Package.state == 'active') \
        .filter(model.Package.private) \
        .all()

    # Lists to hold packages for publishing and notifying
    packages_to_publish = []
    packages_to_notify = []

    # Check each dataset for action
    for package, package_extra in packages:
        # Convert embargo date string to date object. Skip the dataset rather
        # than raising, so one bad value cannot stop every other dataset.
        embargo_date = _parse_embargo_date(package_extra.value)
        if embargo_date is None:
            log.error(
                f"Skipping dataset {package.name}: unreadable embargo date {package_extra.value!r}"
            )
            continue

        if embargo_date <= local_now:
            packages_to_publish.append((package, package_extra))
        elif embargo_date == date_in_7_days:
            packages_to_notify.append((package, package_extra))

    return {"to_publish": packages_to_publish, "to_notify": packages_to_notify}


@logic.validate(logic.schema.default_autocomplete_schema)
def dbca_get_geospatial_coverage(context, data_dict):
    '''
    Get all geospatial coverage choices
    '''
    q = data_dict.get('q')
    limit = data_dict.get('limit')
    return [{"name": spatial.label, "value": json.dumps(spatial.geometry)} for spatial in dbca_model.DbcaSpatial.get_like_label(q, limit)] if q else []


def get_actions():
    return {
        'dbca_get_packages_to_be_published_or_notified': dbca_get_packages_to_be_published_or_notified,
        'dbca_get_geospatial_coverage': dbca_get_geospatial_coverage,
    }
