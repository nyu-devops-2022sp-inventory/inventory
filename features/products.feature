Feature: The pet store service back-end
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

Scenario: List all products
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see "10001", "apple" and "NEW" in the results
    And I should see "10002", "banana" and "NEW" in the results
    And I should not see "10006", "cherry" and "NEW" in the results