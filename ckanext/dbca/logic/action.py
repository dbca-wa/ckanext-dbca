import datetime

import ckan.model as model
import ckan.plugins.toolkit as tk
import ckanext.dbca.logic.schema as schema

from sqlalchemy.sql import func
from ckan.model.package import Package
from ckan.model.package_extra import PackageExtra


@tk.side_effect_free
def dbca_get_sum(context, data_dict):
    tk.check_access(
        "dbca_get_sum", context, data_dict)
    data, errors = tk.navl_validate(
        data_dict, schema.dbca_get_sum(), context)

    if errors:
        raise tk.ValidationError(errors)

    return {
        "left": data["left"],
        "right": data["right"],
        "sum": data["left"] + data["right"]
    }


@tk.side_effect_free
def dbca_get_packages_to_be_published_or_notified(context, data_dict):
    '''
    Get all packages that need to be publshed or need to be notified.
    Notification will be sent for package that will be published in the next 7 days.
    '''
    # Current UTC date
    utc_now = datetime.datetime.utcnow().date()

    # Calculate the date 7 days from now
    date_in_7_days = utc_now + datetime.timedelta(days=7)

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
        # Convert embargo date string to date object
        embargo_date = datetime.datetime.strptime(package_extra.value, '%Y-%m-%d').date()

        if embargo_date <= utc_now:
            packages_to_publish.append((package, package_extra))
        elif embargo_date == date_in_7_days:
            packages_to_notify.append((package, package_extra))

    return {"to_publish": packages_to_publish, "to_notify": packages_to_notify}


def get_actions():
    return {
        'dbca_get_sum': dbca_get_sum,
        'dbca_get_packages_to_be_published_or_notified': dbca_get_packages_to_be_published_or_notified
    }
