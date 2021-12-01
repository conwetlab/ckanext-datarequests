@comments
Feature: Comments

    @comment-add
    Scenario: When a logged-in user submits a comment on a Data Request the comment should then be visible on the Comments tab of the Data Request
        Given "CKANUser" as the persona
        When I log in
        And I go to data request "Test Request" comments
        Then I submit a comment with subject "Test subject" and comment "This is a test comment"
        Then I should see "This is a test comment" within 10 seconds

    @comment-delete
    Scenario: When an Sysadmin visits a data request, they can delete a comment and should not see text 'This comment was deleted.'
        Given "SysAdmin" as the persona
        When I log in
        And I go to data request "Test Request" comments
        And I submit a comment with subject "Comment for deletion" and comment "This is a data request comment to test deletion"
        And I press the element with xpath "//a[contains(@href, '/delete')]/i[contains(@class, 'icon-remove')]"
        Then I should see "Are you sure you want to delete this comment?" within 1 seconds
        Then I press the element with xpath "//button[contains(string(), 'Confirm')]"
        And I should see "Comment has been deleted" within 2 seconds
