# CKAN Data Requests [![Build Status](https://travis-ci.org/conwetlab/ckanext-datarequests.svg?branch=develop)](https://travis-ci.org/conwetlab/ckanext-datarequests) [![Coverage Status](https://coveralls.io/repos/github/conwetlab/ckanext-datarequests/badge.svg?branch=develop)](https://coveralls.io/github/conwetlab/ckanext-datarequests?branch=develop)

CKAN extension that allows users to ask for datasets that are not already published in the CKAN instance. In this way we can set up a Data Market, not only with data supplies but also with data demands.

## How it works

You have two ways for creating, updating, deleting, viewing and closing a datarequest: you can use the graphical interface or the programatic API.

### User Interface
If you prefer to use the graphical interface, you should click on the "Data Requests" section that will appear in the header of your CKAN instance. In this section you'll be able to view the current data requests. In addition, there will be a button that will allow you to create a new data request. In the form that will appear, you will have to introduce the following information:

* **Title**: a title for your data request
* **Description**: a long description for your data request. You should include as much details as you can in order to allow others to understand you needs and upload a dataset that fulfil your requeriments.
* **Organization**: in some cases, you want to ask specific data to an specific organization. If you are in such situation, you should complete this field.

Once that you have created your data request, you can view it by clicking on the link provided when you created it. When you are the owner of a data request, you will also be able to:
* **Close the data request** if you consider that there is a new dataset that fulfil your needs
* **Update the data request** if you can to add/remove some information
* **Delete the data request** if you do not want it to be available any more

### API
On the other hand, you can also use the API. To access this API, you should POST the following URL (as you do for other actions):

``http[s]://[CKAN_HOST]:[CKAN_PORT]/api/action/[ACTION_NAME]``

Here you have a brief description of all the implemented actions:

#### `create_datarequest(context, data_dict)`
Action to create a new data request. This function checks the access rights of the user before creating the data request. If the user is not allowed, a `NotAuthorized` exception will be risen.

In addition, you should note that the parameters will be checked and an exception (`ValidationError`) will be risen if some of these parameters are not valid.

##### Parameters (included in `data_dict`):
* **`title`** (string): the title of the data request
* **`description`** (string): a brief description for your data request
* **`organization_id`** (string): The ID of the organization you want to asign the data request (optional).

##### Returns:
A dict with the data request (`id`, `user_id`, `title`, `description`,`organization_id`, `open_time`, `accepted_dataset`, `close_time`, `closed`, `followers`).


#### `show_datarequest(context, data_dict)`
Action to retrieve the information of a data request. The only required parameter is the `id` of the data request. A `NotFound` exception will be risen if the `id` is not found.

Access rights will be checked before returning the information and an exception will be risen (`NotAuthorized`) if the user is not authorized.

##### Parameters (included in `data_dict`):
* **`id`** (string): the ID of the datarequest to be returned.

##### Returns:
A dict with the data request (`id`, `user_id`, `title`, `description`,`organization_id`, `open_time`, `accepted_dataset`, `close_time`, `closed`, `followers`).


#### `update_datarequest(context, data_dict)`
Action to update a data request. The function checks the access rights of the user before updating the data request. If the user is not allowed, a `NotAuthorized` exception will be risen

In addition, you should note that the parameters will be checked and an exception (`ValidationError`) will be risen if some of these parameters are not valid.

##### Parameters (included in `data_dict`):
* **`id`** (string): the ID of the datarequest to be updated
* **`title`** (string): the updated title of the data request
* **`description`** (string): a updated brief description for your data request
* **`organization_id`** (string): The ID of the organization you want to asign the data request (optional).

##### Returns:
A dict with the data request (`id`, `user_id`, `title`, `description`,`organization_id`, `open_time`, `accepted_dataset`, `close_time`, `closed`, `followers`).


#### `list_datarequests(context, data_dict)`
Returns a list with the existing data requests. Rights access will be checked before returning the results. If the user is not allowed, a `NotAuthorized` exception will be risen

##### Parameters (included in `data_dict`):
* **`organization_id`** (string) (optional): to filter the result by organization
* **`user_id`** (string) (optional): to filter the result by user
* **`closed`** (string) (optional): to filter the result by state (`True`: Closed, `False`: Open)
* **`offset`** (int) (optional) (default `0`): the first element to be returned
* **`limit`** (int) (optional) (default `10`): The max number of data requests to be returned
* **`q`** (string) (optional): to filter the result using a free-text.
* **`sort`** (string) (optional) (default `asc`): `desc` to order data requests in a descending way. `asc` to order data requests in an ascending way.

##### Returns:
A dict with three fields: `result` (a list of data requests), `facets` (a list of the facets that can be used) and `count` (the total number of existing data requests)


#### `delete_datarequest(context, data_dict)`
Action to delete a new data request. The function checks the access rights of the user before deleting the data request. If the user is not allowed, a `NotAuthorized` exception will be risen.

##### Parameters (included in `data_dict`):
* **`id`** (string): the ID of the datarequest to be deleted

##### Returns:
A dict with the data request (`id`, `user_id`, `title`, `description`,`organization_id`, `open_time`, `accepted_dataset`, `close_time`, `closed`, `followers`).


#### `close_datarequest(context, data_dict)`
Action to close a data request. Access rights will be checked before closing the data request. If the user is not allowed, a `NotAuthorized` exception will be risen

##### Parameters (included in `data_dict`):
* **`id`** (string): the ID of the datarequest to be closed
* **`accepted_dataset`** (string): The ID of the dataset accepted as solution for the data request

##### Returns:
A dict with the data request (`id`, `user_id`, `title`, `description`,`organization_id`, `open_time`, `accepted_dataset`, `close_time`, `closed`, `followers`).


#### `comment_datarequest(context, data_dict)`
Action to create a comment in a data request. Access rights will be checked before creating the comment and a `NotAuthorized` exception will be risen if the user is not allowed to create the comment

##### Parameters (included in `data_dict`):
* **`datarequest_id`** (string): the ID of the datarequest to be commented
* **`comment`** (string): The comment to be added to the data request

##### Returns:
A dict with the data request comment (`id`, `user_id`, `datarequest_id`, `time` and `comment`)


#### `show_datarequest_comment(context, data_dict)`
Action to retrieve a comment. Access rights will be checked before getting the comment and a `NotAuthorized` exception will be risen if the user is not allowed to get the comment

##### Parameters (included in `data_dict`):
* **`id`** (string): The ID of the comment to be retrieved

##### Returns:
A dict with the following fields: `id`, `user_id`, `datarequest_id`, `time` and `comment`


#### `list_datarequest_comments(context, data_dict)`
Action to retrieve all the comments of a data request. Access rights will be checked before getting the comments and a `NotAuthorized` exception will be risen if the user is not allowed to read the comments

##### Parameters (included in `data_dict`):
* **`datarequest_id`** (string): The ID of the datarequest whose comments want to be retrieved
* **`sort`** (string) (optional) (default `asc`): `desc` to order comments in a descending way. `asc` to order comments in an ascending way.

##### Returns:
 A list with all the comments of a data request. Every comment is a dict with the following fields: `id`, `user_id`, `datarequest_id`, `time` and `comment`


#### `update_datarequest_comment(context, data_dict)`
Action to update a comment of a data request. Access rights will be checked before updating the comment and a `NotAuthorized` exception will be risen if the user is not allowed to update the comment

##### Parameters (included in `data_dict`):
* **`id`** (string): The ID of the comment to be updated
* **`comment`** (string): The new comment

##### Returns:
A dict with the data request comment (`id`, `user_id`, `datarequest_id`, `time` and `comment`)


#### `delete_datarequest_comment(context, data_dict)`
Action to delete a comment of a data request. Access rights will be checked before deleting the comment and a `NotAuthorized` exception will be risen if the user is not allowed to delete the comment

##### Parameters (included in `data_dict`):
* **`id`** (string): The ID of the comment to be deleted

##### Returns:
A dict with the data request comment (`id`, `user_id`, `datarequest_id`, `time` and `comment`)

#### `follow_datarequest(context, data_dict)`

Action to follow a data request. Access rights will be cheked before following a datarequest and a `NotAuthorized` exception will be risen if the user is not allowed to follow the given datarequest. `ValidationError` will be risen if the datarequest ID is not included or if the user is already following the datarequest. `ObjectNotFound` will be risen if the given datarequest does not exist.

##### Parameters (included in `data_dict`):
* **`id`** (string): The ID of the datarequest to be followed

##### Returns:
`True`

#### `unfollow_datarequest(context, data_dict)`

Action to unfollow a data request. Access rights will be cheked before unfollowing a datarequest and a NotAuthorized exception will be risen if the user is not allowed to unfollow the given datarequest. `ValidationError` will be risen if the datarequest ID is not included in the request. `ObjectNotFound` will be risen if the user is not following the given datarequest.

##### Parameters (included in `data_dict`):
* **`id`** (string): The ID of the datarequest to be unfollowed

##### Returns:
`True`


## Installation

Install this extension in your CKAN instance is as easy as install any other CKAN extension.

* Activate your virtual environment
```
. /usr/lib/ckan/default/bin/activate
```
* Install the extension
```
pip install ckanext-datarequests
```
> **Note**: If you prefer, you can also download the source code and install the extension manually. To do so, execute the following commands:
> ```
> $ git clone https://github.com/conwetlab/ckanext-datarequests.git
> $ cd ckanext-datarequests
> $ python setup.py install
> ```

* Modify your configuration file (generally in `/etc/ckan/default/production.ini`) and add `datarequests` in the `ckan.plugins` property.
```
ckan.plugins = datarequests <OTHER_PLUGINS>
```
* Enable or disable the comments system by setting up the `ckan.datarequests.comments` property in the configuration file (by default, the comments system is enabled).
```
ckan.datarequests.comments = [true|false]
```
* Enable or disable a badge to show the number of data requests in the menu by setting up the `ckan.datarequests.show_datarequests_badge` property in the configuration file (by default, the badge is not shown).
```
ckan.datarequests.show_datarequests_badge = [true|false]
```
* Restart your apache2 reserver
```
sudo service apache2 restart
```
* That's All!

## Translations

Help us to translate this extension so everyone can create data requests. Currently, the extension is translated to English, Spanish, German and Brazilian Portuguese. If you want to contribute with your translation, the first step is to clone this repo and move to the `develop` branch. Then, create the locale for your translation by executing:

```
python setup.py init_catalog -l <YOUR_LOCALE>
```

This will generate a file called `i18n/YOUR_LOCALE/LC_MESSAGES/ckanext-datarequests.po`. This file contains all the untranslated strings. You can manually add a translation for it by editing the `msgstr` section:

```
msgid "This is an untranslated string"
msgstr "This is a itranslated string"
```

Once the translation files (`po`) have been updated, compile them by running:

```
python setup.py compile_catalog
```

This will generate the required `mo` file. Once this file has been generated, commit your changes and create a Pull Request (to the `develop` branch). 

## Tests

This sofware contains a set of test to detect errors and failures. You can run this tests by running the following command (this command will generate coverage reports):
```
python setup.py nosetests
```
**Note:** The `test.ini` file contains a link to the CKAN `test-core.ini` file. You will need to change that link to the real path of the file in your system (generally `/usr/lib/ckan/default/src/ckan/test-core.ini`).

**Note 2:** When creating a PR that includes code changes, please, ensure your new code is tested. No PR will be merged until the Travis CI system marks it as valid.

## Changelog

### v1.1.0

* New: Compatibility with CKAN 2.8.0
* New: Somali translation (thanks to @SimuliChina)

### v1.0.0

* New: Option to follow data requests.
* New: Email notifications:
  * An email will be sent to organization staff when a data request is created in a organization.
  * An email will be sent to followers, people that commented, datarequest creator and organization staff when a comment in a datarequest is created.
  * An email will be sent to followers, people that commented, datarequest creator and organization staff when a data request is closed.
* New: Major API changes:
  * `datarequest_create` :arrow_right: `create_datarequest`
  * `datarequest_show` :arrow_right: `show_datarequest`
  * `datarequest_update` :arrow_right: `update_datarequest`
  * `datarequest_index` :arrow_right: `list_datarequests`
  * `datarequest_delete` :arrow_right: `delete_datarequest`
  * `datarequest_close` :arrow_right: `close_datarequest`
  * `datarequest_comment` :arrow_right: `comment_datarequest`
  * `datarequest_comment_show` :arrow_right: `show_datarequest_comment`
  * `datarequest_comment_list` :arrow_right: `list_datarequest_comments`
  * `datarequest_comment_update` :arrow_right: `update_datarequest_comment`
  * `datarequest_comment_delete` :arrow_right: `delete_datarequest_comment`

### v0.4.1

* New: Brazilian Portuguese translation (thanks to @allysonbarros)

### v0.4.0

* New: Move CI to Travis
* New: Compatibility with CKAN 2.7 (controller adapted by @owl17)

### v0.3.3

* New: German Translation (thanks to @kvlahrosch)

