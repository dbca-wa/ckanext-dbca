import ckan.plugins.toolkit as tk


@tk.auth_allow_anonymous_access
def dbca_get_sum(context, data_dict):
    return {"success": True}


@tk.auth_allow_anonymous_access
@tk.chained_auth_function
def package_create(next_auth, context, data_dict):
    # Only sysadmins can create packages
    return {'success': False, 'msg': 'Only sysadmins can create datasets'}


def get_auth_functions():
    return {
        "dbca_get_sum": dbca_get_sum,
        "package_create": package_create,
    }
