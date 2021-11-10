@comments
Feature: Comments

    @comment-add
    Scenario: When a logged-in user submits a comment on a Data Request the comment should then be visible on the Comments tab of the Data Request
        Given "CKANUser" as the persona
        When I log in
        And I go to data request "Test Request" comments
        Then I should see the add comment form
        Then I submit a comment with subject "Test subject" and comment "This is a test comment"
        Then I should see "This is a test comment" within 10 seconds

    @comment-add @comment-email
    Scenario: When a logged-in user submits a comment on a Data Request the email should contain title and comment
        Given "CKANUser" as the persona
        When I log in
        And I go to data request "Test Request" comments
        Then I should see the add comment form
        Then I submit a comment with subject "Test Request" and comment "This is a test data request comment"
        When I wait for 5 seconds
        Then I should receive a base64 email at "test_org_admin@localhost" containing "Data request subject: Test Request"
        And I should receive a base64 email at "test_org_admin@localhost" containing "Comment: This is a test data request comment"

    @comment-add @comment-profane
    Scenario: When a logged-in user submits a comment containing profanity on a Data Request they should receive an error message and the commment will not appear
        Given "CKANUser" as the persona
        When I log in
        And I go to data request "Test Request" comments
        Then I should see the add comment form
        Then I submit a comment with subject "Test subject" and comment "Soccer balls"
        Then I should see "Comment blocked due to profanity" within 5 seconds

    @comment-report
    Scenario: When a logged-in user reports a comment on a Data Request the comment should be marked as reported and an email notification sent to the organisation admins
        Given "CKANUser" as the persona
        When I log in
        And I go to data request "Test Request" comments
        And I press the element with xpath "//a[contains(string(), 'Report')]"
        Then I should see "Reported" within 5 seconds
        When I wait for 3 seconds
        Then I should receive a base64 email at "test_org_admin@localhost" containing "This comment has been flagged as inappropriate by a user"

    @comment-delete
    Scenario: When an Org Admin visits a data request belonging to their organisation, they can delete a comment and should not see text 'This comment was deleted.'
        Given "TestOrgAdmin" as the persona
        When I log in
        And I go to data request "Test Request" comments
        And I press the element with xpath "//a[@title='Delete comment']"
        Then I should see "Are you sure you want to delete this comment?" within 1 seconds
        Then I press the element with xpath "//button[contains(string(), 'Confirm')]"
        Then I should not see "This comment was deleted." within 2 seconds
        And I should see "Comment deleted by Test Admin." within 2 seconds
