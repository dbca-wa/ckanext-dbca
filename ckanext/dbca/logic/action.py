import ckan.plugins.toolkit as tk
import ckanext.dbca.logic.schema as schema


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


def get_actions():
    return {
        'dbca_get_sum': dbca_get_sum,
    }
