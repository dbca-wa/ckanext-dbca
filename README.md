[![Tests](https://github.com/dbca-wa/ckanext-dbca/workflows/Tests/badge.svg?branch=main)](https://github.com/dbca-wa/ckanext-dbca/actions)

# ckanext-dbca

**TODO:** Put a description of your extension here:  What does it do? What features does it have? Consider including some screenshots or embedding a video!

## Requirements

**TODO:** For example, you might want to mention here which versions of CKAN this
extension works with.

If your extension works across different versions you can add the following table:

Compatibility with core CKAN versions:

| CKAN version    | Compatible?   |
| --------------- | ------------- |
| 2.6 and earlier | not tested    |
| 2.7             | not tested    |
| 2.8             | not tested    |
| 2.9             | not tested    |

Suggested values:

* "yes"
* "not tested" - I can't think of a reason why it wouldn't work
* "not yet" - there is an intention to get it working
* "no"


## Installation

**TODO:** Add any additional install steps to the list below.
   For example installing any non-Python dependencies or adding any required
   config settings.

To install ckanext-dbca:

1. Activate your CKAN virtual environment, for example:

     . /usr/lib/ckan/default/bin/activate

2. Clone the source and install it on the virtualenv

    git clone https://github.com/dbca-wa/ckanext-dbca.git
    cd ckanext-dbca
    pip install -e .
	pip install -r requirements.txt

3. Add `dbca` to the `ckan.plugins` setting in your CKAN
   config file (by default the config file is located at
   `/etc/ckan/default/ckan.ini`).

4. Restart CKAN. For example if you've deployed CKAN with Apache on Ubuntu:

     sudo service apache2 reload


## Config settings

None at present

**TODO:** Document any optional config settings here. For example:

	# The minimum number of hours to wait before re-checking a resource
	# (optional, default: 24).
	ckanext.dbca.some_setting = some_default_value


## Developer installation

To install ckanext-dbca for development, activate your CKAN virtualenv and
do:

    git clone https://github.com/dbca-wa/ckanext-dbca.git
    cd ckanext-dbca
    python setup.py develop
    pip install -r dev-requirements.txt


## Tests

In this project, run extension tests from the CKAN container via `ahoy` so the
CKAN dependencies and config are available.

From the repository root (`dbca-wa`), run all ckanext-dbca tests with:

    ahoy run "cd /srv/app/src_extensions/ckanext-dbca && pytest --ckan-ini /srv/app/config/dbca.ini ckanext/dbca/tests"

To run a single test module, pass the module path to pytest:

    ahoy run "cd /srv/app/src_extensions/ckanext-dbca && pytest --ckan-ini /srv/app/config/dbca.ini ckanext/dbca/tests/test_validators.py"

If you are already inside a CKAN environment with this extension installed and
the test dependencies available, the equivalent direct command is:

    pytest --ckan-ini /srv/app/config/dbca.ini ckanext/dbca/tests


## Releasing a new version of ckanext-dbca

This extension is not published to PyPI. It is installed from git and pinned by
the DBCA CKAN project (`ckan-docker`), which builds the production images. That
project's release checks require the pin to be an immutable, released ref, so a
release here is a prerequisite for a ckan-docker release to master.

Branches: work lands on `develop`; `main` is the released branch.

1. Update the version number in `setup.py`. See [PEP 440](https://peps.python.org/pep-0440/#public-version-identifiers)
   for how to choose one.

2. Raise a release PR from `develop` into `main` and merge it once the checks pass.

3. Tag the merge commit on `main` with the version number from `setup.py`, with no
   `v` prefix, matching the tags used by ckan-docker:

       git checkout main && git pull
       git tag -a 1.0.0 -m "ckanext-dbca 1.0.0"
       git push origin 1.0.0

4. Pin the new tag in ckan-docker, in `ckan/setup/dbca_requirements.sh`:

       pip3 install -e git+https://github.com/dbca-wa/ckanext-dbca.git@${CKANEXT_DBCA_REF:-1.0.0}#egg=ckanext-dbca

   Its `.github/scripts/check-ckanext-dbca-pin.sh` verifies the pin is not a
   branch, is reachable from `main`, and that `develop` is level with `main`.
   Run it locally from the ckan-docker root before raising the release PR there.

Note that the dev image overrides the pin with `CKANEXT_DBCA_REF=develop`, so local
development tracks this branch rather than the released tag.

## License

[AGPL](https://www.gnu.org/licenses/agpl-3.0.en.html)
