import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


import ckanext.dbca.cli as cli
import ckanext.dbca.helpers as helpers
from ckanext.dbca.logic import (action, validators)
from ckanext.doi.interfaces import IDoi

class DbcaPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    # plugins.implements(plugins.IAuthFunctions)
    plugins.implements(plugins.IActions)
    # plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.IClick)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IValidators)
    plugins.implements(IDoi, inherit=True)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")
        toolkit.add_resource("assets", "ckanext_dbca")

    # IAuthFunctions

    # def get_auth_functions(self):
    #     return auth.get_auth_functions()

    # IActions

    def get_actions(self):
        return action.get_actions()

    # IBlueprint

    # def get_blueprint(self):
    #     return views.get_blueprints()

    # IClick

    def get_commands(self):
        return cli.get_commands()

    # ITemplateHelpers

    def get_helpers(self):
        return helpers.get_helpers()

    # IValidators

    def get_validators(self):
        return validators.get_validators()

    # IDoi
    def build_metadata_dict(self, pkg_dict, metadata_dict, errors):
        # Use language set in CKAN config
        try:
            metadata_dict['language'] = toolkit.config['ckanext.doi.language']
        except Exception as e:
            errors['language'] = e
            
        # Remove contributors with empty full_name
        # This is a workaround for when maintainer is not set
        for contributors in metadata_dict['contributors']:
            if not contributors['full_name']:
                metadata_dict['contributors'].remove(contributors)

        return metadata_dict, errors