"""
My Service

Describe what your service does here
"""

from math import prod
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
            version="1.1",
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
# QUERY PRODUCTS(EMPTY FILTER, PRODUCT_NAME, CONDITION)
######################################################################
@app.route("/inventory", methods=["GET"])
def list_products():
    """Returns all of the eligible Products"""
    app.logger.info("Request for product list")
    products = []
    product_name = request.args.get("product_name")
    condition = request.args.get("condition")
    if not product_name and not condition:
        products = Product.all()
    elif product_name and condition:
        products = Product.find_by_name_and_condition(product_name, condition)
    elif product_name:
        products = Product.find_by_name(product_name)
    elif condition:
        products = Product.find_by_condition(condition)

    
    results = [product.serialize() for product in products]
    app.logger.info("Returning %d products", len(results))
    if len(results) == 0:
        raise NotFound("Eligible product was not found.")
    return make_response(jsonify(results), status.HTTP_200_OK)
  
######################################################################
# ADD A NEW PRODUCT
######################################################################
@app.route('/inventory', methods=['POST'])
def create_products():
    """create a new product"""
    app.logger.info('Create Product Request')
    check_content_type("application/json")
    product = Product()
    product.deserialize(request.json)
    find_product = Product.find_by_id_and_condition(product.product_id, product.condition)
    if find_product:
        abort(status.HTTP_409_CONFLICT, 'product {} with condition {} already exist'.format(product.product_id, product.condition))
    product.create()

    location_url = url_for("get_products_with_id", product_id=product.product_id, condition=[product.condition.name], _external=True)

    app.logger.info('Created Product with id: {}'.format(product.product_id))
    return make_response(
        jsonify(product.serialize()),
        status.HTTP_201_CREATED,
        {"Location": location_url}
    )
  
######################################################################
# RETRIEVE A PRODUCT WITH PRODUCT ID
######################################################################
@app.route("/inventory/<int:product_id>", methods=["GET"])
def get_products_with_id(product_id):
    """
    Retrieve Product
    This endpoint will return a Product based on it's id (or with its condition)
    """

    # Check whether we have a condition in args(as query)
    condition = request.args.get("condition")
    products = []
    results = []
    if not condition:
        # For route with only product_id
        app.logger.info("Request for product with id: %s", product_id)
        products = Product.find_by_id(product_id)
        if not products.first():
            raise NotFound("Product with id '{}' was not found.".format(product_id))
        else:
            results = [product.serialize() for product in products]
        app.logger.info("Returning product with id: %s", product_id)
    else:
        # For route with product_id and condition
        app.logger.info("Request for product with id: %s and condition: %s", product_id, condition)
        product = Product.find_by_id_and_condition(product_id, condition)
        if not product:
            raise NotFound('Product {} with condition {} was not found'.format(product_id, condition))
        results.append(product.serialize())
        app.logger.info("Returning product with id: %s and condition: %s", product_id, condition)
    
    # Discard after using Query to unify two situations
    # 
    # products = Product.find_by_id(product_id)
    # if not products:
    #     raise NotFound("Product with id '{}' was not found.".format(product_id))
    # else:
    #     results = [product.serialize() for product in products]
    # app.logger.info("Returning product: %s", product_id)

    return make_response(jsonify(results), status.HTTP_200_OK)

######################################################################
# RETRIEVE A PRODUCT WITH PRODUCT ID AND CONDITION (DISCARD)
######################################################################
# @app.route("/inventory/<int:product_id>/condition/<string:condition>", methods=["GET"])
# def get_products(product_id, condition):
#     """
#     Retrieve a single Product
#     This endpoint will return a Product based on it's id and it's condition
#     """
#     app.logger.info("Request for product with id: %s and condition: %s", product_id, condition)
#     product = Product.find_by_id_and_condition(product_id, condition)
#     if not product:
#         raise NotFound('Product {} with condition {} was not found'.format(product_id, condition))
#     app.logger.info("Returning product: %s", product_id)
#     return make_response(jsonify(product.serialize()), status.HTTP_200_OK)

######################################################################
# DELETE A PRODUCT WITH PRODUCT ID
######################################################################  
@app.route('/inventory/<int:product_id>', methods=['DELETE'])
def delete_products(product_id):
    """delete a product"""
    app.logger.info('Request to delete Product with id: %s', product_id)
    products = []
    products = Product.find_by_id(product_id)
    if not products:
        raise NotFound("Product with id '{}' was not found.".format(product_id))
    else:
        for product in products:
            product.delete()
    return make_response('', status.HTTP_204_NO_CONTENT)

######################################################################
# DELETE A PRODUCT WITH PRODUCT ID AND CONDITION
######################################################################  
@app.route('/inventory/<int:product_id>/condition/<string:condition>', methods=['DELETE'])
def delete_products_with_id(product_id, condition):
    """delete a product"""
    app.logger.info('Request to delete Product with id: %s and condition: %s', product_id, condition)
    product = Product.find_by_id_and_condition(product_id, condition)
    if not product:
        raise NotFound('product {} with condition {} was not found'.format(product_id, condition))
    if product:
        product.delete()
    return make_response('', status.HTTP_204_NO_CONTENT)

######################################################################
# UPDATE AN EXISTING PRODUCT
######################################################################
@app.route('/inventory/<int:product_id>/condition/<string:condition>', methods=['PUT'])
def update_products(product_id, condition):
    """ Update the product """
    app.logger.info('Request to update Product with id: %s and condition: %s', product_id, condition)
    check_content_type("application/json")
    product = Product.find_by_id_and_condition(product_id, condition)
    if not product:
        raise NotFound('product {} with condition {} was not found'.format(product_id, condition))
    product.deserialize(request.json)
    #product.id = product_id
    product.save()

    app.logger.info('Product with id {} updated.'.format(product_id))
    return make_response(jsonify(product.serialize()), status.HTTP_200_OK)

######################################################################
# INCREASE A PRODUCT'S INVENTORY ON DEDICATED CONDITION BY N
######################################################################  
@app.route('/inventory/<int:product_id>/inc', methods=['POST'])
def increase_product_inventory(product_id):
    """increase a product's inventory by a certain value"""
    app.logger.info('Request to increase a product\'s inventory by a certain value with id: %s', product_id)
    condition = request.args.get("condition")
    value = request.args.get("value")
    if not condition or not value:
        abort(status.HTTP_400_BAD_REQUEST, "Value 'condition' and 'value' should be provided")
    try:
        value_int = int(value)
    except ValueError:
        abort(status.HTTP_400_BAD_REQUEST, "'value' not an integer")
    if value_int < 0:
        abort(status.HTTP_400_BAD_REQUEST, "'value should be non-negative")
    product = Product.find_by_id_and_condition(product_id, condition)
    if not product:
        abort(status.HTTP_404_NOT_FOUND, "Product {} with condition {} was not found".format(product_id, condition))
    
    product.quantity += value_int
    product.save()
    return make_response(jsonify(product.serialize()), status.HTTP_200_OK)

######################################################################
# DECREASE A PRODUCT'S INVENTORY ON DEDICATED CONDITION BY N
######################################################################  
@app.route('/inventory/<int:product_id>/dec', methods=['POST'])
def decrease_product_inventory(product_id):
    """decrease a product's inventory by a certain value"""
    app.logger.info('Request to decrease a product\'s inventory by a certain value with id: %s', product_id)
    condition = request.args.get("condition")
    value = request.args.get("value")
    if not condition or not value:
        abort(status.HTTP_400_BAD_REQUEST, "Value 'condition' and 'value' should be provided")
    try:
        value_int = int(value)
    except ValueError:
        abort(status.HTTP_400_BAD_REQUEST, "'value' not an integer")
    if value_int < 0:
        abort(status.HTTP_400_BAD_REQUEST, "'value' should be non-negative")
    product = Product.find_by_id_and_condition(product_id, condition)
    if not product:
        abort(status.HTTP_404_NOT_FOUND, "Product {} with condition {} was not found".format(product_id, condition))
    if value_int > product.quantity:
        abort(status.HTTP_403_FORBIDDEN, "Inventory decreased to negative prohibited.")
    product.quantity -= value_int
    product.save()
    return make_response(jsonify(product.serialize()), status.HTTP_200_OK)


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def check_content_type(media_type):
    """Checks that the media type is correct"""
    content_type = request.headers.get("Content-Type")
    if content_type and content_type == media_type:
        return
    app.logger.error("Invalid Content-Type: %s", content_type)
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        "Content-Type must be {}".format(media_type),
    )
