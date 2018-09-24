# -*- coding: utf-8 -*-

# Copyright (c) 2015-2016 CoNWeT Lab., Universidad Politécnica de Madrid

# This file is part of CKAN Data Requests Extension.

# CKAN Data Requests Extension is free software: you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# CKAN Data Requests Extension is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with CKAN Data Requests Extension. If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, find_packages
import sys, os

version = '1.1.0'

setup(
    name='ckanext-datarequests',
    version=version,
    description="CKAN Extension - Data Requests",
    long_description='''
    CKAN extension that allows users to ask for datasets that are not already published in the CKAN instance. 
    In this way we can set up a Data Market, not only with data supplies but also with data demands.
    ''',
    classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='',
    author='CoNWeT Lab.',
    author_email='amagan@conwet.com',
    url='https://conwet.fi.upm.es',
    download_url='https://github.com/conwetlab/ckanext-datarequests/tarball/v' + version,
    license='GNU Affero General Public License',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=['ckanext', 'ckanext.datarequests'],
    include_package_data=True,
    zip_safe=False,
    setup_requires=['nose>=1.3.0'],
    install_requires=[
        # -*- Extra requirements: -*-
    ],
    tests_require=[
        'nose_parameterized==0.3.3',
        'selenium==2.53',
        'coveralls==1.1'
    ],
    test_suite='nosetests',
    entry_points='''

        [ckan.plugins]
        datarequests=ckanext.datarequests.plugin:DataRequestsPlugin

        [babel.extractors]
        ckan = ckan.lib.extract:extract_ckan
    ''',
    message_extractors={
        'ckanext': [
            ('**.py', 'python', None),
            ('**.js', 'javascript', None),
            ('**/templates/**.html', 'ckan', None),
        ],
    }
)