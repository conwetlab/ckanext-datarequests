import os
from behaving import environment as benv

from behaving.web.steps.browser import named_browser

# Path to the root of the project.
ROOT_PATH = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../'))

# Base URL for relative paths resolution.
BASE_URL = 'http://ckan:3000/'

# URL of remote Chrome instance.
REMOTE_CHROME_URL = 'http://chrome:4444/wd/hub'

# @see .docker/scripts/init.sh for credentials.
PERSONAS = {
    'SysAdmin': dict(
        name=u'admin',
        email=u'admin@localhost',
        password=u'password'
    ),
    'Unathenticated': dict(
        name=u'',
        email=u'',
        password=u''
    ),
    # This user will not be assigned to any organisations
    'CKANUser': dict(
        name=u'ckan_user',
        email=u'ckan_user@localhost',
        password=u'password'
    ),
    'TestOrgAdmin': dict(
        name=u'test_org_admin',
        email=u'test_org_admin@localhost',
        password=u'password'
    ),
    'TestOrgEditor': dict(
        name=u'test_org_editor',
        email=u'test_org_editor@localhost',
        password=u'password'
    ),
    'TestOrgMember': dict(
        name=u'test_org_member',
        email=u'test_org_member@localhost',
        password=u'password'
    ),
    'DataRequestOrgAdmin': dict(
        name=u'dr_admin',
        email=u'dr_admin@localhost',
        password=u'password'
    ),
    'DataRequestOrgEditor': dict(
        name=u'dr_editor',
        email=u'dr_editor@localhost',
        password=u'password'
    ),
    'DataRequestOrgMember': dict(
        name=u'dr_member',
        email=u'dr_member@localhost',
        password=u'password'
    )
}


def before_all(context):
    # The path where screenshots will be saved.
    context.screenshots_dir = os.path.join(ROOT_PATH, 'test/screenshots')
    # The path where file attachments can be found.
    context.attachment_dir = os.path.join(ROOT_PATH, 'test/fixtures')
    # The path where emails can be found.
    context.mail_path = os.path.join(ROOT_PATH, 'test/emails')
    # Set base url for all relative links.
    context.base_url = BASE_URL

    # Always use remote web driver.
    context.remote_webdriver = 1
    context.default_browser = 'chrome'
    context.browser_args = {'url': REMOTE_CHROME_URL}

    # Set the rest of the settings to default Behaving's settings.
    benv.before_all(context)


def after_all(context):
    benv.after_all(context)


def before_feature(context, feature):
    benv.before_feature(context, feature)


def after_feature(context, feature):
    benv.after_feature(context, feature)


def before_scenario(context, scenario):
    benv.before_scenario(context, scenario)
    # Always use remote browser.
    named_browser(context, 'remote')
    # Set personas.
    context.personas = PERSONAS


def after_scenario(context, scenario):
    benv.after_scenario(context, scenario)
