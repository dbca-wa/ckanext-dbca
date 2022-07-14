# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name="ckanext-dbca",
    # If you are changing from the default layout of your extension, you may
    # have to change the message extractors, you can read more about babel
    # message extraction at
    # http://babel.pocoo.org/docs/messages/#extraction-method-mapping-and-configuration
    message_extractors={
        'ckanext': [
            ('**.py', 'python', None),
            ('**.js', 'javascript', None),
            ('**/templates/**.html', 'ckan', None),
        ],
    },
    version='0.0.3',
    author='Florian Mayer',
    author_email='Florian.Mayer@dbca.wa.gov.au',
    url='https://github.com/dbca-wa/ckanext-dbca',
    license='MIT',
    namespace_packages=['ckanext'],
    include_package_data=True,
    packages=['ckanext.dbca'],
    zip_safe=False,
    entry_points='''
    [ckan.plugins]
    dbca=ckanext.dbca.plugin:DbcaPlugin
    ''',
)