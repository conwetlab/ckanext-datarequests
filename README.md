CKAN Data Requests [![Build Status](https://build.conwet.fi.upm.es/jenkins/buildStatus/icon?job=ckan_datarequests)](https://build.conwet.fi.upm.es/jenkins/job/ckan_datarequests/)
=====================

CKAN extension that allows users to ask for datasets that are not already published in the CKAN instance. In this way we can set up a Data Market, not only with data supplies but also with data demands.

How it works
------------
You have two ways for creating, updating, deleting, viewing and closing a datarequest: you can use the graphical interface or the programatic API.

### User Interface
If you prefer to use the graphical interface, you should click on the "Data Requests" section that will appear in the header of your CKAN instance. In this section you'll be able to view the current data requests. In addition, there will be a button that will allow you to create a new data request. In the form that will appear, you will have to introduce the following information:

* **Title**: a title for your data request
* **Description**: a long description for your data request. You should include as much details as you can in order to allow others to understand you needs and upload a dataset that fulfil your requeriments.
* **Organization**: in some cases, you want to ask specific data to an specific organization. If you are in such situation, you should complete this field.

Once that you have created your data request, you can view it by clicking on the link provided when you created it. When you are the owner of a data request, you will also be able of:
* **Closing the data request** if you consider that there is a new dataset that fulfil your needs
* **Updating the data request** if you can to add/remove some information
* **Deleting the data request** if you do not want it to be available any more

### API
On the other hand, you can also use the API. To access this API, you should POST the following URL (as you do for other actions):

``http[s]://[CKAN_HOST]:[CKAN_PORT]/api/action/[ACTION_NAME]``

Here you have a brief description of all the implemented actions:

#### `datarequest_create(context, data_dict)`
Action to create a new data request. This function checks the access rights of the user before creating the data request. If the user is not allowed, a `NotAuthorized` exception will be risen.

In addition, you should note that the parameters will be checked and an exception (`ValidationError`) will be risen if some of these parameters are not valid.

##### Parameters (included in `data_dict`):
* **`title`** (string): the title of the data request
* **`description`** (string): a brief description for your data request
* **`organization_id`** (string): the ID of the organization in case you want to assing the data request to an organization.

##### Returns:
A dict with the data request (`id`, `user_id`, `title`, `description`,`organization_id`, `open_time`, `accepted_dataset`, `close_time`, `closed`).


#### `datarequest_show(context, data_dict)`
Action to retrieve the information of a data request. The only required parameter is the `id` of the data request. A `NotFound` exception will be risen if the `id` is not found.

Access rights will be checked before returning the information and an exception will be risen (`NotAuthorized`) if the user is not authorized.

##### Parameters (included in `data_dict`):
* **`id`** (string): the ID of the datarequest to be displayed

##### Returns:
A dict with the data request (`id`, `user_id`, `title`, `description`,`organization_id`, `open_time`, `accepted_dataset`, `close_time`, `closed`).


#### `datarequest_update(context, data_dict)`
Action to update a dara request. The function checks the access rights of the user before updating the data request. If the user is not allowed, a `NotAuthorized` exception will be risen

In addition, you should note that the parameters will be checked and an exception (`ValidationError`) will be risen if some of these parameters are not valid.

##### Parameters (included in `data_dict`):
* **`id`** (string): the ID of the datarequest to be updated
* **`title`** (string): the title of the data request
* **`description`** (string): a brief description for your data request
* **`organization_id`** (string): the ID of the organization in case you want to assing the data request to an organization.

##### Returns:
A dict with the data request (`id`, `user_id`, `title`, `description`,`organization_id`, `open_time`, `accepted_dataset`, `close_time`, `closed`).


#### `datarequest_index(context, data_dict)`
Returns a list with the existing data requests. Rights access will be checked before returning the results. If the user is not allowed, a `NotAuthorized` exception will be risen

##### Parameters (included in `data_dict`):
* **`organization_id`** (string) (optional): to filter the result by organization
* **`user_id`** (string) (optional): to filter the result by user
* **`closed`** (string) (optional): to filter the result by state (`True`: Closed, `False`: Open)
* **`offset`** (int) (optional) (default `0`): the first element to be returned
* **`limit`** (int) (optional) (default `10`): The max number of data requests to be returned

##### Returns:
A dict with three fields: `result` (a list of data requests), `facets` (a list of the facets that can be used) and `count` (the total number of existing data requests)


#### `datarequest_delete(context, data_dict)`
Action to delete a new dara request. The function checks the access rights of the user before deleting the data request. If the user is not allowed, a `NotAuthorized` exception will be risen.

##### Parameters (included in `data_dict`):
* **`id`** (string): the ID of the datarequest to be deleted

##### Returns:
A dict with the data request (`id`, `user_id`, `title`, `description`,`organization_id`, `open_time`, `accepted_dataset`, `close_time`, `closed`).


#### `datarequest_close(context, data_dict)`
Action to close a data request. Access rights will be checked before closing the data request. If the user is not allowed, a `NotAuthorized` exception will be risen

##### Parameters (included in `data_dict`):
* **`id`** (string): the ID of the datarequest to be closed
* **`accepted_dataset`** (string): The ID of the dataset accepted as solution for the data request

##### Returns:
A dict with the data request (`id`, `user_id`, `title`, `description`,`organization_id`, `open_time`, `accepted_dataset`, `close_time`, `closed`).


#### `datarequest_comment(context, data_dict)`
Action to create a comment in a data request. Access rights will be checked before creating the comment and a `NotAuthorized` exception will be risen if the user is not allowed to create the comment

##### Parameters (included in `data_dict`):
* **`datarequest_id`** (string): the ID of the datarequest to be commented
* **`comment`** (string): The comment to be added to the data request

##### Returns:
A dict with the data request comment (`id`, `user_id`, `datarequest_id`, `time` and `comment`)


#### `datarequest_comment_show(context, data_dict)`
Action to retrieve a comment. Access rights will be checked before getting the comment and a `NotAuthorized` exception will be risen if the user is not allowed to get the comment

##### Parameters (included in `data_dict`):
* **`id`** (string): The ID of the comment to be retrieved

##### Returns:
A dict with the following fields: `id`, `user_id`, `datarequest_id`, `time` and `comment`


#### `datarequest_comment_list(context, data_dict)`
Action to retrieve all the comments of a data request. Access rights will be checked before getting the comments and a `NotAuthorized` exception will be risen if the user is not allowed to read the comments

##### Parameters (included in `data_dict`):
* **`datarequest_id`** (string): The ID of the datarequest whose comments want to be retrieved  

##### Returns:
 A list with all the comments of a data request. Every comment is a dict with the following fields: `id`, `user_id`, `datarequest_id`, `time` and `comment`


#### `datarequest_comment_update(context, data_dict)`
Action to update a comment of a data request. Access rights will be checked before updating the comment and a `NotAuthorized` exception will be risen if the user is not allowed to update the comment

##### Parameters (included in `data_dict`):
* **`id`** (string): The ID of the comment to be updated
* **`comment`** (string): The new comment

##### Returns:
A dict with the data request comment (`id`, `user_id`, `datarequest_id`, `time` and `comment`)


#### `datarequest_comment_delete(context, data_dict)`
Action to delete a comment of a data request. Access rights will be checked before deleting the comment and a `NotAuthorized` exception will be risen if the user is not allowed to delete the comment

##### Parameters (included in `data_dict`):
* **`id`** (string): The ID of the comment to be deleted

##### Returns:
A dict with the data request comment (`id`, `user_id`, `datarequest_id`, `time` and `comment`)

Installation
------------
Install this extension in your CKAN instance is as easy as intall any other CKAN extension.

1. Activate your virtual environment
```
. /usr/lib/ckan/default/bin/activate
```
2. Install the extension
```
pip install ckanext-datarequests
```
 * You can also install the extension by downloading the source from the repository and running `python setup.py install`
3. Modify your configuration file (generally in `/etc/ckan/default/production.ini`) and add `datarequests` in the `ckan.plugins` property.
```
ckan.plugins = datarequests <OTHER_PLUGINS>
```
4. Enable or disable the comments system by setting up the `ckan.datarequests.comments` property in the configuration file (by default, the comments system is enabled).
```
ckan.datarequests.comments = [True|False]
```
5. Enable or disable a badge to show the number of data requests in the menu by setting up the `ckan.datarequests.show_datarequests_badge` property in the configuration file (by default, the badge is not shown).
```
ckan.datarequests.show_datarequests_badge = [True|False]
```
6. Restart your apache2 reserver
```
sudo service apache2 restart
```
7. That's All!

Tests
-----
This sofware contains a set of test to detect errors and failures. You can run this tests by running the following command (this command will generate coverage reports):
```
python setup.py nosetests
```
**Note:** The `test.ini` file contains a link to the CKAN `test-core.ini` file. You will need to change that link to the real path of the file in your system (generally `/usr/lib/ckan/default/src/ckan/test-core.ini`).
