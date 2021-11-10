@data-requests-circumstances
Feature: Datarequest-circumstances

    Scenario: As a sysadmin user when I go to the admin config page I can view the data requests closing circumstances textarea
        Given "SysAdmin" as the persona
        When I log in and go to admin config page
        Then the browser's URL should contain "/ckan-admin/config"
        And I should see "Data request closing circumstances"


    Scenario Outline: Data request creator, Sysadmin and Admin users can see the drop-down field circumstances
        Given "<User>" as the persona
        When I log in and create a datarequest
        And I press the element with xpath "//a[contains(string(), 'Close')]"
        Then the element with the css selector "#field-close_circumstance" should be visible within 1 seconds

        Examples: Users
        | User                  |
        | SysAdmin              |
        | DataRequestOrgAdmin   |


    Scenario Outline: Data request creator, Sysadmin and Admin users, when I select a closing circumstance 'Open dataset already exists', accepted dataset is required
        Given "<User>" as the persona
        When I log in and create a datarequest
        And I press the element with xpath "//a[contains(string(), 'Close')]"
        And I select "Open dataset already exists" from "close_circumstance"
        And I press the element with xpath "//button[contains(string(), 'Close Data Request')]"
        Then I should see an element with the css selector "div.error-explanation.alert.alert-error" within 2 seconds
        And I should see "The form contains invalid entries" within 1 seconds
        And I should see "Accepted dataset cannot be empty" within 1 seconds

        Examples: Users
        | User                  |
        | SysAdmin              |
        | DataRequestOrgAdmin   |


    Scenario Outline: Data request creator, Sysadmin and Admin users, when I select closing circumstance with condition 'To be released as open data at a later date', Approximate publishing date is required
        Given "<User>" as the persona
        When I log in and create a datarequest
        And I press the element with xpath "//a[contains(string(), 'Close')]"
        And I select "To be released as open data at a later date" from "close_circumstance"
        And I press the element with xpath "//button[contains(string(), 'Close Data Request')]"
        Then I should see an element with the css selector "div.error-explanation.alert.alert-error" within 2 seconds
        And I should see "The form contains invalid entries" within 1 seconds
        And I should see "Approximate publishing date cannot be empty" within 1 seconds

        Examples: Users
        | User                  |
        | SysAdmin              |
        | DataRequestOrgAdmin   |


    Scenario Outline: Data request creator, Sysadmin and Admin users, when I select closing circumstance 'Requestor initiated closure', accepted dataset or Approximate publishing date is not required
        Given "<User>" as the persona
        When I log in and create a datarequest
        And I press the element with xpath "//a[contains(string(), 'Close')]"
        And I select "Requestor initiated closure" from "close_circumstance"
        And I press the element with xpath "//button[contains(string(), 'Close Data Request')]"
        Then I should see an element with xpath "//span[contains(@class,'label-closed') and contains(string(), 'Closed')]" within 2 seconds

        Examples: Users
        | User                  |
        | SysAdmin              |
        | DataRequestOrgAdmin   |


    Scenario Outline: Data request creator, Sysadmin and Admin users, when I select closing circumstance 'Open dataset already exists', the Approximate publishing date element is not visible
        Given "<User>" as the persona
        When I log in and create a datarequest
        And I press the element with xpath "//a[contains(string(), 'Close')]"
        And I select "Open dataset already exists" from "close_circumstance"
        Then the element with the css selector "#field-approx_publishing_date" should not be visible within 1 seconds

        Examples: Users
        | User                  |
        | SysAdmin              |
        | DataRequestOrgAdmin   |


    Scenario Outline: Data request creator, Sysadmin and Admin users, when I select closing circumstance 'To be released as open data at a later date', the accepted dataset element is not visible
        Given "<User>" as the persona
        When I log in and create a datarequest
        And I press the element with xpath "//a[contains(string(), 'Close')]"
        And I select "To be released as open data at a later date" from "close_circumstance"
        Then the element with the css selector "#field-accepted_dataset_id" should not be visible within 1 seconds

        Examples: Users
        | User                  |
        | SysAdmin              |
        | DataRequestOrgAdmin   |


    Scenario Outline: Data request creator, Sysadmin and Admin users, when I select closing circumstance 'Data openly available elsewhere', the accepted dataset and Approximate publishing date elements are not visible
        Given "<User>" as the persona
        When I log in and create a datarequest
        And I press the element with xpath "//a[contains(string(), 'Close')]"
        And I select "Data openly available elsewhere" from "close_circumstance"
        Then the element with the css selector "#field-accepted_dataset_id" should not be visible within 1 seconds
        Then the element with the css selector "#field-approx_publishing_date" should not be visible within 1 seconds

        Examples: Users
        | User                  |
        | SysAdmin              |
        | DataRequestOrgAdmin   |


    Scenario Outline: Data request creator, Sysadmin and Admin users, when I close a datarequest with accepted dataset, the accepted dataset should be visible on datarequest page
        Given "<User>" as the persona
        When I log in and create a datarequest
        And I press the element with xpath "//a[contains(string(), 'Close')]"
        And I select "Open dataset already exists" from "close_circumstance"
        # Have to use JS to change the selected value as the behaving framework does not work with autocomplete dropdown
        Then I execute the script "document.getElementById('field-accepted_dataset_id').value = document.getElementById('field-accepted_dataset_id').options[1].value"
        And I press the element with xpath "//button[contains(string(), 'Close Data Request')]"
        Then I should see "Accepted dataset" within 1 seconds
        And I should see "A Wonderful Story" within 1 seconds

        Examples: Users
        | User                  |
        | SysAdmin              |
        | DataRequestOrgAdmin   |


    Scenario Outline: Data request creator, Sysadmin and Admin users, when I close a datarequest with Approximate publishing date, the Approximate publishing date should be visible on datarequest page
        Given "<User>" as the persona
        When I log in and create a datarequest
        And I press the element with xpath "//a[contains(string(), 'Close')]"
        And I select "To be released as open data at a later date" from "close_circumstance"
        And I fill in "approx_publishing_date" with "2025-06-01"
        And I press the element with xpath "//button[contains(string(), 'Close Data Request')]"
        Then I should see "Approximate publishing date" within 1 seconds

        Examples: Users
        | User                  |
        | SysAdmin              |
        | DataRequestOrgAdmin   |

    @wip
    Scenario Outline: Data request creator, Sysadmin and Admin users, when I close a datarequest with closing circumstance 'Requestor initiated closure', the circumstance should be visible on the datarequest page
        Given "<User>" as the persona
        When I log in and create a datarequest
        And I press the element with xpath "//a[contains(string(), 'Close')]"
        And I select "Requestor initiated closure" from "close_circumstance"
        And I press the element with xpath "//button[contains(string(), 'Close Data Request')]"
        Then I should see "Close circumstance" within 1 seconds
        Then I should see "Requestor initiated closure" within 1 seconds

        Examples: Users
        | User                  |
        | SysAdmin              |
        | DataRequestOrgAdmin   |


    Scenario Outline: Data request creator, Sysadmin and Admin users, when I close a datarequest with no accepted dataset or Approximate publishing date, they should not be visible on datarequest page
        Given "<User>" as the persona
        When I log in and create a datarequest
        And I press the element with xpath "//a[contains(string(), 'Close')]"
        And I select "Requestor initiated closure" from "close_circumstance"
        And I press the element with xpath "//button[contains(string(), 'Close Data Request')]"
        Then I should not see "Accepted dataset" within 1 seconds
        Then I should not see "Approximate publishing date" within 1 seconds

        Examples: Users
        | User                  |
        | SysAdmin              |
        | DataRequestOrgAdmin   |
