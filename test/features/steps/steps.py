from behave import step
from behaving.personas.steps import *  # noqa: F401, F403
from behaving.web.steps import *  # noqa: F401, F403
from behaving.web.steps.url import when_i_visit_url
import random
import email
import quopri


@step('I go to homepage')
def go_to_home(context):
    when_i_visit_url(context, '/')


@step('I log in')
def log_in(context):
    assert context.persona
    context.execute_steps(u"""
        When I go to homepage
        And I click the link with text that contains "Log in"
        And I enter my credentials and login
    """)


@step('I enter my credentials and login')
def submit_login(context):
    assert context.persona
    context.execute_steps(u"""
        When I fill in "login" with "$name"
        And I fill in "password" with "$password"
        And I press the element with xpath "//button[contains(string(), 'Login')]"
        Then I should see an element with xpath "//a[@title='Log out']"
    """)


@step('I log in and go to datarequest page')
def log_in_go_to_datarequest(context):
    assert context.persona
    context.execute_steps(u"""
        When I log in
        And I go to datarequest page
    """)


@step('I go to datarequest page')
def go_to_datarequest(context):
    when_i_visit_url(context, '/datarequest')


@step('I fill in title with random text')
def title_random_text(context):
    assert context.persona
    context.execute_steps(u"""
        When I fill in "title" with "Test Title {0}"
    """.format(random.randrange(100000)))


@step(u'I should see the add comment form')
def comment_form_visible(context):
    context.execute_steps(u"""
        Then I should see an element with xpath "//form[contains(@class, 'form')]//input[@name='subject']"
        And I should see an element with xpath "//form[contains(@class, 'form')]//textarea[@name='comment']"
    """)


@step(u'I should not see the add comment form')
def comment_form_not_visible(context):
    context.execute_steps(u"""
        Then I should not see an element with xpath "//form[contains(@class, 'form')]//input[@name='subject']"
        And I should not see an element with xpath "//form[contains(@class, 'form')]//textarea[@name='comment']"
    """)


@step('I go to the data requests page')
def go_to_data_requests_page(context):
    when_i_visit_url(context, '/datarequest')


@step(u'I go to data request "{subject}"')
def go_to_data_request(context, subject):
    context.execute_steps(u"""
        When I go to the data requests page
        And I click the link with text "%s"
        Then I should see "%s" within 5 seconds
    """ % (subject, subject))


@step(u'I go to data request "{subject}" comments')
def go_to_data_request_comments(context, subject):
    context.execute_steps(u"""
        When I go to data request "%s"
        And I click the link with text that contains "Comments"
    """ % (subject))


@step(u'I submit a comment with subject "{subject}" and comment "{comment}"')
def submit_comment_with_subject_and_comment(context, subject, comment):
    """
    There can be multiple comment forms per page (add, edit, reply) each with fields named "subject" and "comment"
    This step overcomes a limitation of the fill() method which only fills a form field by name
    :param context:
    :param subject:
    :param comment:
    :return:
    """
    context.browser.execute_script("""
        subject_field = document.querySelector('form input[name="subject"]');
        if (subject_field) { subject_field.value = '%s'; }
        """ % subject)
    context.browser.execute_script("""
        document.querySelector('form textarea[name="comment"]').value = '%s';
        """ % comment)
    context.browser.execute_script("""
        document.querySelector('form .btn-primary[type="submit"]').click();
        """)


@step(u'I submit a reply with comment "{comment}"')
def submit_reply_with_comment(context, comment):
    """
    There can be multiple comment forms per page (add, edit, reply) each with fields named "subject" and "comment"
    This step overcomes a limitation of the fill() method which only fills a form field by name
    :param context:
    :param comment:
    :return:
    """
    context.browser.execute_script("""
        document.querySelector('.comment-wrapper form textarea[name="comment"]').value = '%s';
        """ % comment)
    context.browser.execute_script("""
        document.querySelector('.comment-wrapper form .btn-primary[type="submit"]').click();
        """)


# The default behaving step does not convert base64 emails
# Modifed the default step to decode the payload from base64
@step(u'I should receive a base64 email at "{address}" containing "{text}"')
def should_receive_base64_email_containing_text(context, address, text):
    def filter_contents(mail):
        mail = email.message_from_string(mail)
        payload = mail.get_payload()
        payload += "=" * ((4 - len(payload) % 4) % 4)  # do fix the padding error issue
        decoded_payload = quopri.decodestring(payload).decode('base64')
        print('decoded_payload: ', decoded_payload)
        return text in decoded_payload

    assert context.mail.user_messages(address, filter_contents)


@step('I log in and go to admin config page')
def log_in_go_to_admin_config(context):
    assert context.persona
    context.execute_steps(u"""
        When I log in
        And I go to admin config page
    """)


@step('I go to admin config page')
def go_to_admin_config(context):
    when_i_visit_url(context, '/ckan-admin/config')


@step('I log in and create a datarequest')
def log_in_create_a_datarequest(context):
    assert context.persona
    context.execute_steps(u"""
        When I log in and go to datarequest page
        And I click the link with text that contains "Add Data Request"
        And I fill in title with random text
        And I fill in "description" with "Test description"
        And I select "open-data-administration-data-requests" from "organization_id"
        And I press the element with xpath "//button[contains(string(), 'Create Data Request')]"
    """)
