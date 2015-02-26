CKAN Data Requests [![Build Status](https://build.conwet.fi.upm.es/jenkins/buildStatus/icon?job=ckan_datarequests)](https://build.conwet.fi.upm.es/jenkins/job/ckan_datarequests/)
=====================

CKAN extension that allows users to ask for datasets that are not already published in the CKAN instance. In this way we can set up a Data Market, not only with data supplies but also with data demands.


Installation
------------
Install this extension in your CKAN instance is as easy as intall any other CKAN extension.

* Download the source from this GitHub repo.
* Activate your virtual environment (generally by running `. /usr/lib/ckan/default/bin/activate`)
* Install the extension by running `python setup.py develop`
* Modify your configuration file (generally in `/etc/ckan/default/production.ini`) and add `datarequests` in the `ckan.plugins` setting. 
* Restart your apache2 reserver (`sudo service apache2 restart`)
* That's All!

Tests
-----
This sofware contains a set of test to detect errors and failures. You can run this tests by running the following command:
```
nosetests --ckan --with-pylons=test.ini ckanext/datarequests/tests/
```
**Note:** The `test.ini` file contains a link to the CKAN `test-core.ini` file. You will need to change that link to the real path of the file in your system (generally `/usr/lib/ckan/default/src/ckan/test-core.ini`). 

You can also generate coverage reports by running:
```
nosetests --ckan --with-xunit --with-pylons=test.ini ckanext/datarequests/tests/ --with-coverage --cover-package=ckanext.datarequests --cover-inclusive --cover-erase . --cover-xml
