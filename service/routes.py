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

@app.route('/products', methods=['POST'])
def create_products():
    """create a new product"""
    app.logger.info('Create Product Request')
    product = Product()
    product.deserialize(request.get_json)
    product.create()
    app.logger.info('Created Product with id: {}'.format(product.id))
    return make_response(jsonify(product.serialize()),
                        status.HTTP_201_CREATED,
                        {'location': url_for('get_products', product_id = product.id, _external=True)})

@app.route('/products/<int:product_id>', methods=['DELETE'])
def delete_products(product_id):
    "delete a product"
    app.logger.info('Request to delete Product with id: {}'.format(product_id))
    product = Product.find_or_404()
    if product:
        product.delete()
    return make_response('', status.HTTP_204_NO_CONTENT)



