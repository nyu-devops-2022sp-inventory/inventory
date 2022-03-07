"""
My Service

Describe what your service does here
"""

import os
import sys
import logging
from flask import Flask, jsonify, request, url_for, make_response, abort
from . import status  # HTTP Status Codes

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
    return (
        "Reminder: return some useful information in json format about the service here",
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
