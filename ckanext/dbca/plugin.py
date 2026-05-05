import logging

import ckan.model as model
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.plugins.interfaces import IMiddleware

from ckanext.dbca import cli, views, helpers
from ckanext.dbca.logic import action, validators
from ckanext.doi.interfaces import IDoi
from ckanext.dbca.db_log_handler import configure_logging
from ckanext.dbca.model import dbca_logs

log = logging.getLogger(__name__)


class DbcaPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.IClick)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IValidators)
    plugins.implements(IDoi, inherit=True)
    plugins.implements(IMiddleware)

    # IConfigurer

    def update_config_schema(self, schema):
        ignore_missing = toolkit.get_validator('ignore_missing')
        dbca_validate_geojson = toolkit.get_validator('dbca_validate_geojson')

        schema.update({
            'ckanext.dbca.default_map_coordinates': [ignore_missing, dbca_validate_geojson]
        })

        return schema

    def update_config(self, config_):
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")
        toolkit.add_resource("assets", "ckanext_dbca")
        if dbca_logs.exists():
            configure_logging()

    # IMiddleware
    def make_middleware(self, app, config):
        """Make the middleware for the app."""
        @app.after_request
        def _rollback_orm_after_server_error(response):
            # Error handlers (e.g. for InternalServerError)
            # Roll back on 5xx so a failed ORM transaction is not left open.
            if response is not None and response.status_code >= 500:
                try:
                    model.Session.rollback()
                except Exception:
                    log.exception(
                        "ckanext-dbca: could not roll back ORM after 5xx response"
                    )
            return response

        @app.teardown_request
        def _rollback_orm_on_unhandled_exception(exc):
            # Unhandled exceptions (e.g. for RuntimeError)
            # Roll back on unhandled exceptions so a failed ORM transaction is not left open.
            if exc is None:
                return
            try:
                model.Session.rollback()
            except Exception:
                log.exception(
                    "ckanext-dbca: could not roll back ORM after unhandled request error"
                )

        return app

    # IActions

    def get_actions(self):
        return action.get_actions()

    # IBlueprint

    def get_blueprint(self):
        return views.get_blueprints()

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
        language = toolkit.config.get('ckanext.doi.language', 'en')
        metadata_dict['language'] = language

        # Remove contributors with empty full_name
        # This is a workaround for when maintainer is not set
        for contributors in metadata_dict['contributors']:
            if not contributors['full_name']:
                metadata_dict['contributors'].remove(contributors)

        return metadata_dict, errors
