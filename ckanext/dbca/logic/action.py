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
def dbca_get_datasets_to_be_published(context, data_dict):
    datasets = model.Session.query(Package, PackageExtra) \
                            .join(PackageExtra, Package.id == PackageExtra.package_id) \
                            .filter(PackageExtra.key == 'embargo') \
                            .filter(func.date(PackageExtra.value) <= func.date(datetime.datetime.utcnow())) \
                            .filter(Package.state == 'active') \
                            .all()

    return datasets


@tk.side_effect_free
def dbca_get_datasets_to_be_notified(context, data_dict):
    # Calculate the date 7 days from now and the end of that day
    date_in_7_days = datetime.datetime.utcnow().date() + datetime.timedelta(days=7)
    start_of_day = datetime.datetime.combine(date_in_7_days, datetime.time.min)
    end_of_day = datetime.datetime.combine(date_in_7_days, datetime.time.max)

    # Query the datasets
    datasets = model.Session.query(model.Package, model.PackageExtra) \
                            .join(model.PackageExtra, model.Package.id == model.PackageExtra.package_id) \
                            .filter(model.PackageExtra.key == 'embargo') \
                            .filter(func.date(model.PackageExtra.value) >= start_of_day) \
                            .filter(func.date(model.PackageExtra.value) <= end_of_day) \
                            .filter(model.Package.state == 'active') \
                            .all()

    return datasets


def get_actions():
    return {
        'dbca_get_sum': dbca_get_sum,
        'dbca_get_datasets_to_be_published': dbca_get_datasets_to_be_published,
        'dbca_get_datasets_to_be_notified': dbca_get_datasets_to_be_notified,
    }
