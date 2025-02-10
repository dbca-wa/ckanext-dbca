import ckan.plugins.toolkit as tk


@tk.auth_allow_anonymous_access
def dbca_get_sum(context, data_dict):
    return {"success": True}


def get_auth_functions():
    return {
        "dbca_get_sum": dbca_get_sum
    }
