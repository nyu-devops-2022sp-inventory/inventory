"""
My Service

Describe what your service does here
"""

from math import prod
import os
from queue import Empty
import sys
import logging
from venv import create
from attr import validate
from flask import Flask, jsonify, request, url_for, make_response, abort
from flask_restx import Api, Resource, fields, reqparse, inputs
from numpy import integer
from service.models import Product, Condition, DataValidationError
from . import status  # HTTP Status Codes
from werkzeug.exceptions import NotFound

# For this example we'll use SQLAlchemy, a popular ORM that supports a
# variety of backends including SQLite, MySQL, and PostgreSQL
from flask_sqlalchemy import SQLAlchemy
from service.models import Product, DataValidationError

# Import Flask application
from . import app


######################################################################
# Configure the Root route before OpenAPI
######################################################################
@app.route("/")
def index():
    """ Index page """
    app.logger.info("Request for Index page(Root URL)")
    return app.send_static_file("index.html")


######################################################################
# Configure Swagger before initializing it
######################################################################
api = Api(app,
          version='1.0.0',
          title='Inventory REST API Service',
          description='This is the inventory server.',
          default='products',
          default_label='Inventory operations',
          doc='/apidocs', # default also could use doc='/apidocs/'
          prefix=''
         )

# Define the model so that the docs reflect what can be sent
create_model = api.model('Product', {
    'product_id': fields.Integer(required=True,
                          description='The id of the Product'),
    'product_name': fields.String(required=True,
                              description='The name of Product'),
    'quantity': fields.Integer(required=True,
                              description='The quantity of Product'),                          
    'condition': fields.String(required=False,
                              enum=Condition._member_names_, 
                              description='The condition of the Product'),
    'restock_level': fields.Integer(required=True,
                              description='The restock level of Product'), 
    'reorder_amount': fields.Integer(required=True,
                              description='The reorder amount of Product')

})

product_model = api.inherit(
    'ProductModel', 
    create_model,
    {
        'id': fields.String(readOnly=True,
                            description='The unique id assigned internally by service'),
    }
)

# product_model = api.model('Product', {
#     'product_id': fields.Integer(required=True,
#                           description='The id of the Product'),
#     'product_name': fields.String(required=True,
#                               description='The name of Product'),
#     'quantity': fields.Integer(required=True,
#                               description='The quantity of Product'),                          
#     'condition': fields.String(required=False,
#                               enum=Condition._member_names_, 
#                               description='The condition of the Product'),

# })

# query string arguments
product_args = reqparse.RequestParser()
# product_args.add_argument('product_id', type=str, required=False, help='List Products by id')
product_args.add_argument('product_name', type=str, required=False, help='List Product by name')
product_args.add_argument('condition', type=str, required=False, help='List Products by condition')
product_args.add_argument('value', type=str, required=False, help='Doing action on quantity')


# quantity_args = reqparse.RequestParser()
# quantity_args.add_argument('condition', type=str, required=True, help='List Products by condition')
# quantity_args.add_argument('value', type=str, required=True, help='Doing action on quantity')

######################################################################
# Special Error Handlers
######################################################################
@api.errorhandler(DataValidationError)
def request_validation_error(error):
    """ Handles Value Errors from bad data """
    message = str(error)
    app.logger.error(message)
    return {
        'status_code': status.HTTP_400_BAD_REQUEST,
        'error': 'Bad Request',
        'message': message
    }, status.HTTP_400_BAD_REQUEST





######################################################################
#  PATH: /inventory/<int:product_id>/
######################################################################
@api.route('/inventory/<int:product_id>')
@api.param('product_id', 'The Product identifier')
class ProductResource(Resource):
    """
    ProductResource class
    Allows the manipulation of a single Product
    GET /{product_id} - Returns a Product with the id
    PUT /pet{id} - Update a Product with the id
    DELETE /pet{id} -  Deletes a Product with the id
    """
    #------------------------------------------------------------------
    # RETRIEVE A PRODUCT & SEARCH PRODUCT(S)
    #------------------------------------------------------------------
    @api.doc('get_products')
    @api.response(404, 'Product not found')
    @api.marshal_with(product_model)
    @api.expect(product_args, validate=True)
    def get(self, product_id):
        """
        Retrieve Product
        This endpoint will return a Product based on it's id and its condition
        """
        """
        Search Product
        This endpoint will return Product(s) based on the id, condition and/or name  
        """
        # Check whether we have a condition in args(as query)
        args = product_args.parse_args()
        condition = args.get("condition")
        results = []

        # For route with only product_id
        if not args['condition']:
            app.logger.info("Request for product with id: %s", product_id)
            products = Product.find_by_id(product_id)
            if not products.first():
                abort(status.HTTP_404_NOT_FOUND, "Product with id '{}' was not found.".format(product_id))
                # raise NotFound("Product with id '{}' was not found.".format(product_id))
            else:
                results = [product.serialize() for product in products]
            app.logger.info("Returning product with id: %s", product_id)
        else:
            app.logger.info("Request for product with id: %s and condition: %s", product_id, condition)
            if condition not in ['NEW', 'OPEN_BOX', 'USED', 'UNKNOWN']:
                abort(status.HTTP_400_BAD_REQUEST, "'condition' not valid")
            product = Product.find_by_id_and_condition(product_id, condition)
            if not product:
                abort(status.HTTP_404_NOT_FOUND, "Product with id '{}' was not found.".format(product_id))
                # raise NotFound('Product {} with condition {} was not found'.format(product_id, condition))
            else:
                results = product.serialize()
            app.logger.info("Returning product: %s", product_id)

        return results, status.HTTP_200_OK

    #------------------------------------------------------------------
    # UPDATE AN EXISTING PRODUCT
    #------------------------------------------------------------------
    @api.doc('update_products')
    @api.response(404, 'Product not found')
    @api.response(400, 'The posted Product data was not valid')
    @api.expect(product_model)
    @api.marshal_with(product_model)
    def put(self, product_id):
        """ Update the product """
        condition = request.args.get("condition")

        app.logger.info('Request to update Product with id: %s and condition: %s', product_id, condition)
        check_content_type("application/json")
        if condition not in ['NEW', 'OPEN_BOX', 'USED', 'UNKNOWN']:
            abort(status.HTTP_400_BAD_REQUEST, "'condition' not valid")
        product = Product.find_by_id_and_condition(product_id, condition)
        if not product:
            abort(status.HTTP_404_NOT_FOUND, "Product {} with condition {} was not found".format(product_id, condition))
        if product.product_name != request.json["product_name"]:
            abort(status.HTTP_400_BAD_REQUEST, "Product Name Conflict") 
        if str(product.product_id) != str(request.json["product_id"]):
            abort(status.HTTP_400_BAD_REQUEST, "Product ID Conflict") 
        data = api.payload
        product.deserialize(data)
        check_and_reorder_product(product)
        product.save()

        app.logger.info('Product with id {} updated.'.format(product_id))
        return product.serialize(), status.HTTP_200_OK

    #------------------------------------------------------------------
    # DELETE A PET
    #------------------------------------------------------------------
    @api.doc('delete_pets')
    @api.response(204, 'Product deleted')
    def delete(self, product_id):
        """delete a product"""
        app.logger.info('Request to delete Product with id: %s', product_id)
        products = []
        products = Product.find_by_id(product_id)
        if not products.first():
            raise NotFound("Product with id '{}' was not found.".format(product_id))
        else:
            for product in products:
                product.delete()
        return '', status.HTTP_204_NO_CONTENT



######################################################################
#  PATH: /inventory
######################################################################
@api.route('/inventory', strict_slashes=False)
class ProductCollection(Resource):
    """ Handles all interactions with collections of Products """

    #------------------------------------------------------------------
    # LIST ALL PRODUCTS (ALL or with query parameters)
    #------------------------------------------------------------------
    @api.doc('list_products')
    @api.expect(product_args, validate=True)
    @api.marshal_list_with(product_model)
    def get(self):
        """Returns all of the eligible Products"""
        app.logger.info("Request for product list ...")
        products = []
        args = product_args.parse_args()
        if not args["product_name"] and not args["condition"]:
            products = Product.all()
        elif args["product_name"] and args["condition"]:
            if args["condition"] not in ['NEW', 'OPEN_BOX', 'USED', 'UNKNOWN']:
                abort(status.HTTP_400_BAD_REQUEST, "'condition' not valid")
            products = Product.find_by_name_and_condition(args["product_name"], args["condition"])
        elif args["product_name"]:
            products = Product.find_by_name(args["product_name"])
        elif args["condition"]:
            if args["condition"] not in ['NEW', 'OPEN_BOX', 'USED', 'UNKNOWN']:
                abort(status.HTTP_400_BAD_REQUEST, "'condition' not valid")
            products = Product.find_by_condition(args["condition"])

        
        results = [product.serialize() for product in products]
        app.logger.info("Returning %d products", len(results))
        return results, status.HTTP_200_OK

    #------------------------------------------------------------------
    # ADD A NEW PRODUCT
    #------------------------------------------------------------------
    @api.doc('create_products')
    @api.response(400, 'The posted Product data was not valid')
    @api.response(409, 'The posted Product already exists')
    @api.expect(create_model)
    @api.marshal_with(product_model, code=201)
    def post(self):
        """create a new product"""
        app.logger.info('Create Product Request')
        check_content_type("application/json")
        product = Product()
        product.deserialize(api.payload)
        
        find_product = Product.find_by_id_and_condition(product.product_id, product.condition)
        if find_product:
            abort(status.HTTP_409_CONFLICT, 'product {} with condition {} already exists'.format(product.product_id, product.condition))
        product.create()

        location_url = url_for("product_resource", product_id=product.product_id, condition = product.condition.name, _external=True)

        app.logger.info('Created Product with id: {}'.format(product.product_id))
        return product.serialize(), status.HTTP_201_CREATED, {"Location": location_url}

######################################################################
#  PATH: /inventory/<int:product_id>/inc
######################################################################
@api.route('/inventory/<int:product_id>/inc')
@api.param('product_id', 'The Product identifier')

class IncreaseResource(Resource):
    """ Increase the quantity of a Product """

    @api.doc('increase_products')
    @api.response(400, 'The posted Product data was not valid')
    @api.response(404, 'Product not found')
    @api.expect(product_args, validate=True)
    def put(self, product_id):
        """increase a product's inventory by a certain value"""
        app.logger.info('Request to increase a product\'s inventory by a certain value with id: %s', product_id)
        args = product_args.parse_args()
        # condition = args.get("condition")
        # value = args.get("value")
        if not args['condition'] or not args['value']:
            abort(status.HTTP_400_BAD_REQUEST, "Value 'condition' and 'value' should be provided")
        try:
            value_int = int(args['value'])
        except ValueError:
            abort(status.HTTP_400_BAD_REQUEST, "'value' not an integer")
        if value_int < 0:
            abort(status.HTTP_400_BAD_REQUEST, "'value' should be non-negative")
        if args['condition'] not in ['NEW', 'OPEN_BOX', 'USED', 'UNKNOWN']:
            abort(status.HTTP_400_BAD_REQUEST, "'condition' not valid")
        product = Product.find_by_id_and_condition(product_id, args['condition'])
        if not product:
            abort(status.HTTP_404_NOT_FOUND, "Product {} with condition {} was not found".format(product_id, args['condition']))
        
        product.quantity += value_int
        check_and_reorder_product(product)
        product.save()
        return product.serialize(), status.HTTP_200_OK

######################################################################
#  PATH: /inventory/<int:product_id>/dec
######################################################################
@api.route('/inventory/<int:product_id>/dec')
@api.param('product_id', 'The Product identifier')

class DecreaseResource(Resource):
    """ Decrease the quantity of a Product """

    @api.doc('decrease_products')
    @api.response(400, 'The posted Product data was not valid')
    @api.response(403, 'Inventory decreased to negative prohibited.') 
    @api.response(404, 'Product not found')   
    @api.expect(product_args, validate=True)
    def put(self, product_id):
        """decrease a product's inventory by a certain value"""
        app.logger.info('Request to decrease a product\'s inventory by a certain value with id: %s', product_id)
        args = product_args.parse_args()
        condition = args.get("condition")
        value = args.get("value")
        if not condition or not value:
            abort(status.HTTP_400_BAD_REQUEST, "Value 'condition' and 'value' should be provided")
        try:
            value_int = int(value)
        except ValueError:
            abort(status.HTTP_400_BAD_REQUEST, "'value' not an integer")
        if value_int < 0:
            abort(status.HTTP_400_BAD_REQUEST, "'value' should be non-negative")
        if condition not in ['NEW', 'OPEN_BOX', 'USED', 'UNKNOWN']:
            abort(status.HTTP_400_BAD_REQUEST, "'condition' not valid")
        product = Product.find_by_id_and_condition(product_id, condition)
        if not product:
            abort(status.HTTP_404_NOT_FOUND, "Product {} with condition {} was not found".format(product_id, condition))
        if value_int > product.quantity:
            abort(status.HTTP_403_FORBIDDEN, "Inventory decreased to negative prohibited.")
        product.quantity -= value_int
        check_and_reorder_product(product)
        product.save()
        return product.serialize(), status.HTTP_200_OK

######################################################################
#  PATH: /inventory/<int:product_id>/update
######################################################################
@api.route('/inventory/<int:product_id>/update')
@api.param('product_id', 'The Product identifier')
class UpdateResource(Resource):

    @api.doc('update_products')
    @api.response(400, 'The posted Product data was not valid')
    @api.response(404, 'Product not found')
    @api.expect(product_args, validate=True)
    def put(self,product_id):
        """update a product's inventory by a certain value"""
        app.logger.info('Request to update a product\'s inventory with a certain value with id: %s', product_id)
        args = product_args.parse_args()
        # condition = args.get("condition")
        # value = args.get("value")
        if not args['condition'] or not args['value']:
            abort(status.HTTP_400_BAD_REQUEST, "Value 'condition' and 'value' should be provided")
        try:
            value_int = int(args['value'])
        except ValueError:
            abort(status.HTTP_400_BAD_REQUEST, "'value' not an integer")
        if value_int < 0:
            abort(status.HTTP_400_BAD_REQUEST, "'value' should be non-negative")
        if args['condition'] not in ['NEW', 'OPEN_BOX', 'USED', 'UNKNOWN']:
                abort(status.HTTP_400_BAD_REQUEST, "'condition' not valid")
        product = Product.find_by_id_and_condition(product_id, args['condition'])
        if not product:
            abort(status.HTTP_404_NOT_FOUND, "Product {} with condition {} was not found".format(product_id, args['condition']))

        product.quantity = value_int
        check_and_reorder_product(product)
        product.save()
        return product.serialize(), status.HTTP_200_OK





# ######################################################################
# # QUERY PRODUCTS(EMPTY FILTER, PRODUCT_NAME, CONDITION)
# ######################################################################
# @app.route("/inventory", methods=["GET"])
# def list_products():
#     """Returns all of the eligible Products"""
#     app.logger.info("Request for product list")
#     products = []
#     product_name = request.args.get("product_name")
#     condition = request.args.get("condition")
#     if not product_name and not condition:
#         products = Product.all()
#     elif product_name and condition:
#         products = Product.find_by_name_and_condition(product_name, condition)
#     elif product_name:
#         products = Product.find_by_name(product_name)
#     elif condition:
#         products = Product.find_by_condition(condition)

    
#     results = [product.serialize() for product in products]
#     app.logger.info("Returning %d products", len(results))
#     # if len(results) == 0:
#     #     raise NotFound("Eligible product was not found.")
#     return make_response(jsonify(results), status.HTTP_200_OK)
  
# ######################################################################
# # ADD A NEW PRODUCT
# ######################################################################
# @app.route('/inventory', methods=['POST'])
# def create_products():
#     """create a new product"""
#     app.logger.info('Create Product Request')
#     check_content_type("application/json")
#     product = Product()
#     product.deserialize(request.json)
    
#     find_product = Product.find_by_id_and_condition(product.product_id, product.condition)
#     if find_product:
#         abort(status.HTTP_409_CONFLICT, 'product {} with condition {} already exist'.format(product.product_id, product.condition))
#     product.create()

#     location_url = url_for("get_products", product_id=product.product_id, condition = product.condition.name, _external=True)

#     app.logger.info('Created Product with id: {}'.format(product.product_id))
#     return make_response(
#         jsonify(product.serialize()),
#         status.HTTP_201_CREATED,
#         {"Location": location_url}
#     )
  
# ######################################################################
# # SEARCH PRODUCT(S) WITH PRODUCT ID
# ######################################################################
# @app.route("/inventory/<int:product_id>", methods=["GET"])
# def get_products(product_id):
#     """
#     Retrieve Product
#     This endpoint will return a Product based on it's id (or with its condition)
#     """

#     # Check whether we have a condition in args(as query)
#     condition = request.args.get("condition")
#     results = []
#     # For route with only product_id
#     if not condition:
#         app.logger.info("Request for product with id: %s", product_id)
#         products = Product.find_by_id(product_id)
#         if not products.first():
#             raise NotFound("Product with id '{}' was not found.".format(product_id))
#         else:
#             results = [product.serialize() for product in products]
#         app.logger.info("Returning product with id: %s", product_id)
#     else:
#         app.logger.info("Request for product with id: %s and condition: %s", product_id, condition)
#         product = Product.find_by_id_and_condition(product_id, condition)
#         if not product:
#             raise NotFound('Product {} with condition {} was not found'.format(product_id, condition))
#         else:
#             results = product.serialize()
#         app.logger.info("Returning product: %s", product_id)

#     return make_response(jsonify(results), status.HTTP_200_OK)


# ######################################################################
# # DELETE A PRODUCT WITH PRODUCT ID
# ######################################################################  
# @app.route('/inventory/<int:product_id>', methods=['DELETE'])
# def delete_products(product_id):
#     """delete a product"""
#     app.logger.info('Request to delete Product with id: %s', product_id)
#     products = []
#     products = Product.find_by_id(product_id)
#     if not products.first():
#         raise NotFound("Product with id '{}' was not found.".format(product_id))
#     else:
#         for product in products:
#             product.delete()
#     return make_response('', status.HTTP_204_NO_CONTENT)


# ######################################################################
# # UPDATE AN EXISTING PRODUCT
# ######################################################################
# @app.route('/inventory/<int:product_id>', methods=['PUT'])
# def update_products(product_id):
#     """ Update the product """
#     condition = request.args.get("condition")

#     app.logger.info('Request to update Product with id: %s and condition: %s', product_id, condition)
#     check_content_type("application/json")
#     product = Product.find_by_id_and_condition(product_id, condition)
#     if not product:
#         abort(status.HTTP_404_NOT_FOUND, "Product {} with condition {} was not found".format(product_id, condition))
#     if product.product_name != request.json["product_name"]:
#         abort(status.HTTP_400_BAD_REQUEST, "Product Name Conflict") 
#     if str(product.product_id) != str(request.json["product_id"]):
#         abort(status.HTTP_400_BAD_REQUEST, "Product ID Conflict") 
#     product.deserialize(request.json)
#     check_and_reorder_product(product)
#     #product.id = product_id
#     product.save()

#     app.logger.info('Product with id {} updated.'.format(product_id))
#     return make_response(jsonify(product.serialize()), status.HTTP_200_OK)

# ######################################################################
# # UPDATE A PRODUCT'S INVENTORY TO N
# ######################################################################
# @app.route('/inventory/<int:product_id>/update', methods=['PUT'])
# def update_product_inventory(product_id):
#     """update a product's inventory by a certain value"""
#     app.logger.info('Request to update a product\'s inventory with a certain value with id: %s', product_id)
#     condition = request.args.get("condition")
#     value = request.args.get("value")
#     if not condition or not value:
#         abort(status.HTTP_400_BAD_REQUEST, "Value 'condition' and 'value' should be provided")
#     try:
#         value_int = int(value)
#     except ValueError:
#         abort(status.HTTP_400_BAD_REQUEST, "'value' not an integer")

#     product = Product.find_by_id_and_condition(product_id, condition)
#     if not product:
#         abort(status.HTTP_404_NOT_FOUND, "Product {} with condition {} was not found".format(product_id, condition))

#     product.quantity = value_int
#     check_and_reorder_product(product)
#     product.save()
#     return make_response(jsonify(product.serialize()), status.HTTP_200_OK)

# ######################################################################
# # INCREASE A PRODUCT'S INVENTORY ON DEDICATED CONDITION BY N
# ######################################################################  
# @app.route('/inventory/<int:product_id>/inc', methods=['PUT'])
# def increase_product_inventory(product_id):
#     """increase a product's inventory by a certain value"""
#     app.logger.info('Request to increase a product\'s inventory by a certain value with id: %s', product_id)
#     condition = request.args.get("condition")
#     value = request.args.get("value")
#     if not condition or not value:
#         abort(status.HTTP_400_BAD_REQUEST, "Value 'condition' and 'value' should be provided")
#     try:
#         value_int = int(value)
#     except ValueError:
#         abort(status.HTTP_400_BAD_REQUEST, "'value' not an integer")
#     if value_int < 0:
#         abort(status.HTTP_400_BAD_REQUEST, "'value' should be non-negative")
#     product = Product.find_by_id_and_condition(product_id, condition)
#     if not product:
#         abort(status.HTTP_404_NOT_FOUND, "Product {} with condition {} was not found".format(product_id, condition))
    
#     product.quantity += value_int
#     check_and_reorder_product(product)
#     product.save()
#     return make_response(jsonify(product.serialize()), status.HTTP_200_OK)

# ######################################################################
# # DECREASE A PRODUCT'S INVENTORY ON DEDICATED CONDITION BY N
# ######################################################################  
# @app.route('/inventory/<int:product_id>/dec', methods=['PUT'])
# def decrease_product_inventory(product_id):
#     """decrease a product's inventory by a certain value"""
#     app.logger.info('Request to decrease a product\'s inventory by a certain value with id: %s', product_id)
#     condition = request.args.get("condition")
#     value = request.args.get("value")
#     if not condition or not value:
#         abort(status.HTTP_400_BAD_REQUEST, "Value 'condition' and 'value' should be provided")
#     try:
#         value_int = int(value)
#     except ValueError:
#         abort(status.HTTP_400_BAD_REQUEST, "'value' not an integer")
#     if value_int < 0:
#         abort(status.HTTP_400_BAD_REQUEST, "'value' should be non-negative")
#     product = Product.find_by_id_and_condition(product_id, condition)
#     if not product:
#         abort(status.HTTP_404_NOT_FOUND, "Product {} with condition {} was not found".format(product_id, condition))
#     if value_int > product.quantity:
#         abort(status.HTTP_403_FORBIDDEN, "Inventory decreased to negative prohibited.")
#     product.quantity -= value_int
#     check_and_reorder_product(product)
#     product.save()
#     return make_response(jsonify(product.serialize()), status.HTTP_200_OK)


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################

def init_db():
    """ Initializes the SQLAlchemy app """
    global app
    Product.init_db(app)
    print("init database sucessfully")


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


def check_and_reorder_product(product):
    """check if condition of product is new and the quantity of product is lower than the restock level, than reorder product
    """
    if product.condition.name == "NEW" and product.quantity < product.restock_level:
        app.logger.info("restock product")
        product.quantity += product.reorder_amount
