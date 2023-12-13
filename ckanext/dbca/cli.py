import ckan.lib.helpers as helpers
import ckan.plugins.toolkit as tk
import ckanext.dbca.helpers as dbca_helpers
import logging
import datetime
import click

log = logging.getLogger(__name__)


@click.group(short_help="DBCA CLI Commands")
def dbca():
    pass


@dbca.command('scheduled_datasets')
@click.pass_context
def scheduled_datasets(ctx):
    datasets = tk.get_action('dbca_get_datasets_to_be_published_or_notified')({})
    flask_app = ctx.meta['flask_app']
    aus_tz = tk.h.get_display_timezone()

    with flask_app.test_request_context():
        for dataset, extras in datasets.get('to_publish', []):
            log.info(
                f"Dataset {dataset.name} is scheduled to be published at {extras.value}"
            )
            log.info(f"Current time is {datetime.datetime.now(aus_tz)}")
            try:
                dataset_name = dataset.name
                log.info(f"Scheduling Dataset {dataset_name} to be published")
                data_dict = tk.get_action('package_show')(
                    {u"ignore_auth": True}, {'id': dataset.id}
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
                tk.abort(
                    403, tk._('Not authorized to perform bulk update')
                )
                log.error(
                    f'Error scheduled_datasets {dataset_name}: Site user not authorized to perform bulk update'
                )
            except Exception as e:
                tk.error_shout(e)
                log.error(f'Error scheduled_datasets {dataset_name}: {e}')

        # Email notification.
        emails_to_notify = {}
        # Loop through datasets, and build the email list to be notified from given package
        for package, package_extras in datasets.get('to_notify', []):
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


def get_commands():
    return [
        dbca
    ]
