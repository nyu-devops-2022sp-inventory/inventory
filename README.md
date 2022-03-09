# inventory
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

This repository is for inventory group in NYU-DevOps-2022sp class

## Introduction
The inventory resource keeps track of how many of each product we have in our warehouse. Now, it can reference a product, the quantity and the condition of the item (i.e., new, open box, used)on hand. Inventory will also track restock levels in the future. Restock levels will help us know when to order more products.

**Version 1.0 overview:**
1. Define the object model in inventory as **products** with attribute id/product_name/quantity/status .
2. Implement the CREATE/READ/UPDATE/DELETE/LIST API.
3. Allow the microservice root URL ('/') should return some useful information about the service like the name, version, and what our resource URL is.
4. Have a portable environment for development
5. Apply **nosetests** in development process and get coverage of 97%.
6. Use Docker and a docker-compose.yml file with the Remote Containers extensions for services like PostgreSQL. So that they are running in Docker.


## Prerequisite Software Installation

This microservice uses Docker and Visual Studio Code with the Remote Containers extension to provide a consistent repeatable disposable development environment.
You will need the following software installed:

- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [Visual Studio Code](https://code.visualstudio.com)
- [Remote Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension from the Visual Studio Marketplace

All of these can be installed manually by clicking on the links above or you can use a package manager like **Homebrew** on Mac of **Chocolatey** on Windows.

## Bring up the development environment

To bring up the development environment you should clone this repo, change into the repo directory:

```bash
$ git clone https://github.com/nyu-devops-2022sp-inventory/inventory.git
$ cd inventory
$ code .
```

## Running the tests

Run the tests using `nosetests`

- If you are using Windows OS, try
```shell
$ nosetests --exe
```

- For MacOS, try
```shell
$ nosetests
```

Nose is also configured to automatically run the `coverage` tool and you should see a percentage-of-coverage report at the end of your tests. If you want to see what lines of code were not tested use:

```shell
$ coverage report -m
```

This is particularly useful because it reports the line numbers for the code that have not been covered so you know which lines you want to target with new test cases to get higher code coverage.

## Running the service

To start the service simply use:

```shell
$ flask run
```

You should be able to reach the service at: http://localhost:8000. The port that is used is controlled by an environment variable defined in the `.flaskenv` file which Flask uses to load it's configuration from the environment by default.

After entering the root, you can see a json file return to you with content:

```shell
{
  "list_path": "http://127.0.0.1:8000/products", 
  "name": "Inventory REST API Service", 
  "version": "1.0"
}
```
That means you sucessfully start the microservice.

## Make some REST calls

With the service running, open a second `bash` terminal and issue the following `curl` commands:

List all products:

```bash
curl -X GET http://127.0.0.01:8000/products 
```

Create a product:

```bash
curl -X POST \
  http://127.0.0.01:8000/products \
  -H 'content-type: application/json' \
  -d '{"name":"apple", "quantity":2, "status":"NEW"}'
```

Read a product(hint: change the <product_id> into a real id number):

```bash
curl -X GET \
  http://127.0.0.01:8000/products/<product_id>
```

Update a product:

```bash
curl -X PUT \
  http://127.0.0.01:8000/products/<product_id> \
  -H 'content-type: application/json' \
  -d '{"name":"Green apple", "quantity":2, "status":"NEW"}'
```

Delete a product:

```bash
curl -X DELETE http://127.0.0.01:8000/products/<product_id>
```

## Bring down the development environment

There is no need to manually bring the development environment down. When you close Visual Studio Code it will wait a while to see if you load it back up and if you don't it will stop the Docker containers. When you come back again, it will start them up and resume where you left off.
