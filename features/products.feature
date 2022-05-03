Feature: The product store service back-end
    As a Inventory Manager
    I need a RESTful catalog service
    So that I can keep track of all my products

Background: 
    Given the following products
        | product_id | product_name     | condition | quantity  | restock_level  | reorder_amount |
        | 10001      | apple            | NEW       | 20        | 10             | 15             |
        | 10001      | apple            | USED      | 20        | 10             | 15             |
        | 10002      | banana           | NEW       | 24        | 10             | 15             |
        | 10003      | lemon            | NEW       | 38        | 5              | 10             |
        | 10004      | orange           | NEW       | 15        | 8              | 10             |
        | 10005      | apple            | NEW       | 20        | 10             | 15             |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Inventory REST API Service" in the title
    And I should not see "404 Not Found"

Scenario: List all product
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see "10001", "apple" and "NEW" in the results
    And I should see "10001", "apple" and "USED" in the results
    And I should see "10002", "banana" and "NEW" in the results
    And I should see "10003", "lemon" and "NEW" in the results
    And I should see "10004", "orange" and "NEW" in the results
    And I should see "10005", "apple" and "NEW" in the results
    And I should not see "10006", "cherry" and "NEW" in the results

Scenario: Search for Apples
    When I visit the "Home Page"
    And I set the "Product Name" to "apple"
    And I press the "Search" button
    Then I should see "10001", "apple" and "NEW" in the results
    And I should see "10001", "apple" and "USED" in the results
    And I should see "10005", "apple" and "NEW" in the results
    And I should not see "10006", "cherry" and "NEW" in the results

Scenario: Search for "NEW" Product
    When I visit the "Home Page"
    And I select "New" in the "Condition" dropdown
    And I press the "Search" button
    Then I should see "10001", "apple" and "NEW" in the results
    And I should see "10002", "banana" and "NEW" in the results
    And I should not see "10001", "apple" and "USED" in the results

Scenario: Search for "NEW" Apples
    When I visit the "Home Page"
    And I set the "Product Name" to "apple"
    And I select "New" in the "Condition" dropdown
    And I press the "Search" button
    Then I should see "10001", "apple" and "NEW" in the results
    And I should see "10005", "apple" and "NEW" in the results
    And I should not see "10001", "apple" and "USED" in the results

Scenario: Retrieve a Product
    When I visit the "Home Page"
    And I set the "Product ID" to "10001"
    And I select "New" in the "Condition" dropdown
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "apple" in the "Product Name" field
    And I should see "20" in the "Quantity" field
    And I should see "New" in the "Condition" dropdown
    And I should see "10" in the "Restock Level" field
    And I should see "15" in the "Reorder Amount" field

Scenario: Create a Product
    When I visit the "Home Page"
    And I set the "Product ID" to "10006"
    And I select "New" in the "Condition" dropdown
    And I set the "Product Name" to "green apple"
    And I set the "Quantity" to "20"
    And I set the "Restock Level" to "5"
    And I set the "Reorder Amount" to "10"
    And I press the "Create" button
    Then I should see the message "Success"
    When I press the "Clear" button
    Then the "Product ID" field should be empty
    And the "Condition" field should be empty
    When I set the "Product ID" to "10006"
    And I select "New" in the "Condition" dropdown
    And I press the "Search" button
    Then I should see "10006", "green apple" and "NEW" in the results

Scenario: Delete a Product
    When I visit the "Home Page"
    And I set the "Product ID" to "10001"
    And I press the "Delete" button
    Then I should see the message "Product has been Deleted"
    And the "Product ID" field should be empty
    And the "Condition" field should be empty
    When I press the "Search" button
    Then I should not see "10001", "apple" and "USED" in the results
    And I should not see "10001", "apple" and "NEW" in the results
    And I should see "10002", "banana" and "NEW" in the results

Scenario: Update a Product:
    When I visit the "Home Page"
    And I set the "Product ID" to "10001"
    And I select "New" in the "Condition" dropdown
    And I set the "Product Name" to "tapple"
    And I press the "Update" button
    Then I should see the message "Product Name Conflict"
    When I press the "Clear" button
    Then the "Product ID" field should be empty
    And the "Condition" field should be empty
    When I set the "Product ID" to "10001"
    And I select "New" in the "Condition" dropdown
    And I press the "Retrieve" button
    Then I should see "20" in the "Quantity" field
    When I set the "Quantity" to "30"
    And I press the "Update" button
    Then I should see the message "Success"
    When I press the "Retrieve" button
    Then I should see "30" in the "Quantity" field

Scenario: Increase a Product's Quantity:
    When I visit the "Home Page"
    And I set the "Product ID" to "10001"
    And I select "New" in the "Condition" dropdown
    And I set the "Change Value" to "5"
    And I press the "Increase" button
    Then I should see the message "Success"
    And I should see "25" in the "Quantity" field
    When I set the "Change Value" to "-5"
    And I press the "Increase" button
    Then I should see the message "'value' should be non-negative"

Scenario: Increase a Product's Quantity:
    When I visit the "Home Page"
    And I set the "Product ID" to "10001"
    And I select "New" in the "Condition" dropdown
    And I set the "Change Value" to "5"
    And I press the "Decrease" button
    Then I should see the message "Success"
    And I should see "15" in the "Quantity" field
    When I set the "Change Value" to "-5"
    And I press the "Decrease" button
    Then I should see the message "'value' should be non-negative"
