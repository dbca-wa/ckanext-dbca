import datetime
import click
import os
import json
import geojson

import ckan.lib.helpers as helpers
import ckan.plugins.toolkit as tk
import ckanext.dbca.helpers as dbca_helpers
import logging
import ckan.model as model
import ckanext.dbca.model as dbca_model

log = logging.getLogger(__name__)


@click.group(short_help="DBCA CLI Commands")
def dbca():
    pass


@dbca.command('scheduled_datasets')
@click.pass_context
def scheduled_datasets(ctx):
    packages = tk.get_action('dbca_get_packages_to_be_published_or_notified')({})
    flask_app = ctx.meta['flask_app']
    aus_tz = tk.h.get_display_timezone()

    with flask_app.test_request_context():
        for package, package_extras in packages.get('to_publish', []):
            log.info(
                f"Dataset {package.name} is scheduled to be published at {package_extras.value}"
            )
            log.info(f"Current time is {datetime.datetime.now(aus_tz)}")
            try:
                dataset_name = package.name
                log.info(f"Scheduling Dataset {dataset_name} to be published")
                data_dict = tk.get_action('package_show')(
                    {u"ignore_auth": True}, {'id': package.id}
                )
                site_user = tk.get_action(u"get_site_user")(
                    {u"ignore_auth": True}, {}
                )
                context = {u"user": site_user[u"name"]}
                # set the dataset to Public
                data_dict['private'] = False
                # set the embargo date to null
                data_dict.pop('embargo')
                tk.get_action('package_update')(context, data_dict)
                log.info(f"Dataset {dataset_name} is public")
            except tk.NotAuthorized:
                tk.error_shout('Not authorized to perform bulk update')
                log.error(
                    f'Error scheduled_datasets {dataset_name}: Site user not authorized to perform bulk update'
                )
            except Exception as e:
                tk.error_shout(e)
                log.error(f'Error scheduled_datasets {dataset_name}: {e}')

        # Email notification.
        emails_to_notify = {}
        # Loop through datasets, and build the email list to be notified from given package
        for package, package_extras in packages.get('to_notify', []):
            try:
                log.info(
                    f"Send email notification for scheduled dataset {package.name} to be published at {package_extras.value}"
                )

                # Get email addresses.
                package_emails = dbca_helpers.extract_emails_from_package(package)
                for email, name in package_emails:
                    # Initialize the list for this email if it's not already there
                    if email not in emails_to_notify:
                        emails_to_notify[email] = []

                    # Add the current dataset to the list of datasets for this email
                    emails_to_notify[email].append((email, name, package, package_extras))
            except Exception as ex:
                log.error(ex)

        # Loop through emails and the notification
        for email in emails_to_notify:
            for recipient_email, recipient_name, package, package_extras in emails_to_notify.get(email, (None, None, None, None)):
                if not recipient_email and not package and not package_extras:
                    continue

                if not recipient_name:
                    recipient_name = recipient_email

                try:
                    email_subject = tk.render('emails/subject/scheduled_dataset_notification.txt', {})
                    body = tk.render(
                        'emails/bodies/scheduled_dataset_notification.txt',
                        {
                            'package_name': package.title,
                            'package_url': helpers.url_for('dataset.read', id=package.id, _external=True),
                            'release_date': package_extras.value
                        }
                    )

                    tk.mail_recipient(
                        recipient_name,
                        recipient_email,
                        email_subject,
                        body
                    )
                except Exception as ex:
                    log.error(ex)


@dbca.command('load_spatial_data')
def load_spatial_data():
    '''
    This function loads spatial data from a directory specified in the CKAN configuration
    and applies mappings to the data. It iterates over the spatial data files in the directory,
    validates the data, and adds it to the database if it meets certain criteria.
    '''
    spatial_data_path = tk.config.get('ckanext.dbca.spatial_data_path')
    log.info("Loading spatial data")
    if not spatial_data_path or not os.path.exists(spatial_data_path):
        log.error(f"Spatial data directory {spatial_data_path} not found")
        return
    spatial_data_mappings = json.loads(tk.config.get('ckanext.dbca.spatial_data_mappings', '{}'))
    if not spatial_data_mappings:
        log.error("Spatial data mappings not found")
        return

    for spatial_data_file in spatial_data_mappings:
        geojson_file = os.path.join(spatial_data_path, spatial_data_file)
        if not os.path.exists(geojson_file):
            log.error(f"Spatial data file {spatial_data_file} not found")
            continue

        log.info(f"Loading spatial data from {geojson_file}")
        with open(geojson_file, 'r') as file:
            try:
                data = geojson.load(file)
                if not data.is_valid:
                    log.error(f"Invalid spatial data file {spatial_data_file}")
                    continue
                spatial_data_mapping = spatial_data_mappings.get(spatial_data_file)
            except Exception:
                log.error(f"Error loading spatial data file {spatial_data_file}")
                continue
            for item in data.get('features', []):
                if spatial_data_mapping.get('code') in item.get('properties', {}) and spatial_data_mapping.get('name') in item.get('properties', {}):
                    name = item.get('properties', {}).get(spatial_data_mapping.get('name'))
                    if not name:
                        continue
                    code = item.get('properties', {}).get(spatial_data_mapping.get('code', '')) or ''
                    layer = spatial_data_mapping.get('layer')
                    label = f"{name.title()} ({code.title()}, {layer})"
                    if dbca_model.DbcaSpatial.get_by_label(label):
                        continue
                    geometry = item.get('geometry')
                    dbca_spatial = dbca_model.DbcaSpatial(label=label, geometry=geometry)
                    log.info(f"Adding spatial data for {label}")
                    model.Session.add(dbca_spatial)
                    model.Session.commit()

    log.info("Spatial data loaded")


def get_commands():
    return [
        dbca
    ]
