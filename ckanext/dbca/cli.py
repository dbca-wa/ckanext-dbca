import ckan.plugins.toolkit as tk
import ckan.lib.helpers as helpers
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
    datasets = tk.get_action('dbca_get_datasets_to_be_published')({})
    flask_app = ctx.meta['flask_app']

    with flask_app.test_request_context():
        for dataset, extras in datasets:
            if extras.key == 'embargo':
                aus_tz = tk.h.get_display_timezone()
                localized_date = helpers._datestamp_to_datetime(extras.value)
                log.info(
                    f"Dataset {dataset.name} is scheduled to be published at {extras.value} UTC which is {localized_date} {aus_tz}"
                )
                log.info(f"Current time is {datetime.datetime.now(aus_tz)}")
                if localized_date <= datetime.datetime.now(aus_tz):
                    try:
                        dataset_name = dataset.name
                        log.info(
                            f"Scheduling Dataset {dataset_name} to be published"
                        )
                        data_dict = tk.get_action('package_show')(
                            {u"ignore_auth": True}, {'id': dataset.id})
                        site_user = tk.get_action(u"get_site_user")(
                            {u"ignore_auth": True}, {})
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


@dbca.command('send_email_notification_for_scheduled_datasets')
@click.pass_context
def send_email_notification_for_scheduled_datasets(ctx):
    datasets = tk.get_action('dbca_get_datasets_to_be_notified')({})
    flask_app = ctx.meta['flask_app']

    with flask_app.test_request_context():
        for dataset, extras in datasets:
            if extras.key == 'embargo':
                aus_tz = tk.h.get_display_timezone()
                localized_date = helpers._datestamp_to_datetime(extras.value)
                log.info(
                    f"Dataset {dataset.name} is scheduled to be published at {extras.value} UTC which is {localized_date} {aus_tz}"
                )
                log.info(f"Current time is {datetime.datetime.now(aus_tz)}, send email notification")
                if localized_date <= datetime.datetime.now(aus_tz):
                    try:
                        # Get email addresses.
                        recipient_name = 'awang'
                        recipient_email = 'awang.setyawan@salsa.digital'

                        dataset_name = dataset.name
                        log.info(f"Email is sent for dataset {dataset_name}")

                        if not recipient_name or not recipient_email:
                            tk.abort(403, tk._('No recipient configured'))

                        email_subject = tk.render('emails/subject/scheduled_dataset_notification.txt', {})
                        body = tk.render(
                            'emails/bodies/scheduled_dataset_notification.txt',
                            {
                                # 'full_name': user.fullname,
                                # 'package_name': pkg_dict.get('title'),
                                # 'package_url': url_for('dataset.read', id=pkg_dict.get('id'), _external=True),
                                # 'org_name': org_dict.get('title')
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
