@data-requests
Feature: Datarequest

    Scenario: Data Requests are accessible via the /datarequest URL
        When I go to datarequest page
        Then the browser's URL should contain "/datarequest"


    Scenario: When visiting the datarequests page as a non-logged in user, the 'Add Data Request' button is not visible
        When I go to datarequest page
        Then I should not see an element with xpath "//a[contains(string(), 'Add data request', 'i')]"


    Scenario: Data requests submitted without a description will produce an error message
        Given "SysAdmin" as the persona
        When I log in and go to datarequest page
        And I click the link with text that contains "Add Data Request"
        And I fill in "title" with "Test data request"
        And I press the element with xpath "//button[contains(string(), 'Create Data Request')]"
        Then I should see an element with the css selector "div.error-explanation.alert.alert-error" within 2 seconds
        And I should see "The form contains invalid entries" within 1 seconds
        And I should see an element with the css selector "span.error-block" within 1 seconds
        And I should see "Description cannot be empty" within 1 seconds


    Scenario Outline: Data request creator and Sysadmin can see a 'Close' button on the data request detail page for opened data requests
        Given "<User>" as the persona
        When I log in and go to datarequest page
        And I press "Test Request"
        Then I should see an element with xpath "//a[contains(string(), 'Close')]"

        Examples: Users
        | User                  |
        | SysAdmin              |


    Scenario Outline: Non admin users cannot see a 'Close' button on the data request detail page for opened data requests
        Given "<User>" as the persona
        When I log in and go to datarequest page
        And I press "Test Request"
        Then I should not see an element with xpath "//a[contains(string(), 'Close')]"

        Examples: Users
        | User                  |
        | CKANUser              |
        | DataRequestOrgEditor  |
        | DataRequestOrgMember  |
        | TestOrgAdmin          |
        | TestOrgEditor         |
        | TestOrgMember         |


    Scenario: Creating a new data request will show the data request afterward
        Given "TestOrgEditor" as the persona
        When I log in and create a datarequest
        Then I should see "Open" within 1 seconds
        And I should see an element with xpath "//a[contains(string(), 'Close')]"


    Scenario: Closing a data request will show the data request afterward
        Given "DataRequestOrgAdmin" as the persona
        When I log in and create a datarequest
        And I press the element with xpath "//a[contains(string(), 'Close')]"
        And I select "Requestor initiated closure" from "close_circumstance"
        And I press the element with xpath "//button[contains(string(), 'Close Data Request')]"
        Then I should see "Closed" within 1 seconds
        And I should not see an element with xpath "//a[contains(string(), 'Close')]"
