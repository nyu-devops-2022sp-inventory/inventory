"""
My Service

Describe what your service does here
"""

import os
import sys
import logging
from flask import Flask, jsonify, request, url_for, make_response, abort
from . import status  # HTTP Status Codes
from werkzeug.exceptions import NotFound

# For this example we'll use SQLAlchemy, a popular ORM that supports a
# variety of backends including SQLite, MySQL, and PostgreSQL
from flask_sqlalchemy import SQLAlchemy
from service.models import Product, DataValidationError

# Import Flask application
from . import app

######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """ Root URL response """
    app.logger.info("Request for Root URL")
    return (
        jsonify(
            name="Inventory REST API Service",
            version="1.0",
            list_path=url_for("list_products", _external=True),
            # update_path=url_for("update_product", _external=False),
        ),
        status.HTTP_200_OK,
    )


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def init_db():
    """ Initializes the SQLAlchemy app """
    global app
    Product.init_db(app)
    print("init database sucessfully")


######################################################################
# LIST ALL PRODUCTS
######################################################################
@app.route("/products", methods=["GET"])
def list_products():
    """Returns all of the Pets"""
    app.logger.info("Request for product list")
    products = []
    products = Product.all()
    results = [product.serialize() for product in products]
    app.logger.info("Returning %d products", len(results))
    return make_response(jsonify(results), status.HTTP_200_OK)


######################################################################
# RETRIEVE A PRODUCT
######################################################################
@app.route("/products/<int:product_id>", methods=["GET"])
def get_products(product_id):
    """
    Retrieve a single Product
    This endpoint will return a Product based on it's id
    """
    app.logger.info("Request for product with id: %s", product_id)
    product = Product.find_or_404(product_id)
    if not product:
        raise NotFound("Product with id '{}' was not found.".format(product_id))
    app.logger.info("Returning pet: %s", product.product_name)
    return make_response(jsonify(product.serialize()), status.HTTP_200_OK)


######################################################################
# UPDATE AN EXISTING PRODUCT
######################################################################
@app.route('/products/<int:product_id>', methods=['PUT'])
def update_products(product_id):
    """ Update the quantity of product """
    app.logger.info('Request to update Product with id: {} by {}'.format(product_id, quantity))

    product = Product.find(product_id)
    if not product:
        return make_response('Product with id {} was not found.'.format(product_id), status.HTTP_404_NOT_FOUND)

    product.quantity += quantity
    product.save()

    app.logger.info('Product with id {} increases {}.'.format(product_id, quantity))
    return product.serialize(), status.HTTP_200_OK
