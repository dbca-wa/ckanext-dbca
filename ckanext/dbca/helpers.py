import ckan.model as model
import json
import os


def extract_emails_from_package(package):
    '''
    Extract author, maintainer and organization admin emails from package
    '''
    emails = set()

    # Extract author email
    author_email = getattr(package, 'author_email', None)
    author_name = getattr(package, 'author', None)
    if author_email:
        emails.add((author_email, author_name))

    # Extract maintainer email
    maintainer_email = getattr(package, 'maintainer_email', None)
    maintainer_name = getattr(package, 'maintainer', None)
    if maintainer_email:
        emails.add((maintainer_email, maintainer_name))

    # Extract organization admin emails
    if not package.owner_org:
        return emails

    org = model.Group.get(package.owner_org)
    if not org:
        return emails

    for user in org.member_all:
        if not user.capacity == 'admin' or not user.is_active():
            continue

        user_obj = model.User.get(user.table_id)
        if user_obj and user_obj.email:
            emails.add((user_obj.email, user_obj.fullname))

    return emails


def spatial_choices(field):
    data = []
    file_path = os.path.join(os.path.dirname(__file__), 'geospatial_coverage.json')
    with open(file_path, 'r') as file:
        data = json.load(file)

    choice_list = []
    for item in data:
        choice_list.append({
            'label': item['label'],
            'value': json.dumps(item['value'], separators=(',', ':'))
        })

    return choice_list


def get_helpers():
    return {
        "extract_emails_from_package": extract_emails_from_package,
        "spatial_choices": spatial_choices,
    }
