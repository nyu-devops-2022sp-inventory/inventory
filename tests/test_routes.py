"""
TestProduct API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from unittest.mock import MagicMock, patch
from urllib.parse import quote_plus
from werkzeug.exceptions import NotFound
from service import status  # HTTP Status Codes
from service.models import db, Product, init_db, Condition
from service.routes import app
from .factories import ProductFactory

# Disable all but critical errors during normal test run
# uncomment for debugging failing tests
#logging.disable(logging.CRITICAL)

# DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///../db/test.db')
DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@postgres:5432/testdb"
)
BASE_URL = "/inventory"
CONTENT_TYPE_JSON = "application/json"

######################################################################
#  T E S T   C A S E S
######################################################################
class TestProductServer(TestCase):
    """ REST API Server Tests """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        db.session.close()

    def setUp(self):
        """ This runs before each test """
        db.drop_all()  # clean up the last tests
        db.create_all()  # create new tables
        self.app = app.test_client()

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()
        db.drop_all()

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """ Test index call """
        resp = self.app.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def _create_products(self, count):
        """Factory method to create products in bulk"""
        products = []
        for _ in range(count):
            test_product = ProductFactory()
            resp = self.app.post(
                BASE_URL, json=test_product.serialize(), content_type=CONTENT_TYPE_JSON
            )
            self.assertEqual(
                resp.status_code, status.HTTP_201_CREATED
            )
            new_product = resp.get_json()
            test_product.id = new_product["id"]
            products.append(test_product)
        return products

    def test_get_product_list(self):
        """Get a list of Products"""
        self._create_products(5)
        resp = self.app.get(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 5)

    def test_query_product_list_by_name(self):
        """Query Products by name"""
        products = self._create_products(10)
        test_name = products[0].product_name
        name_products = [product for product in products if product.product_name == test_name]
        resp = self.app.get(
            BASE_URL, query_string="name={}".format(quote_plus(test_name))
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(name_products))
        # check the data just to be sure
        for product in data:
            self.assertEqual(product["name"], test_name)
    
    def test_query_products_with_not_exist_name(self):
        """Query Products by non-exist name"""
        products = self._create_products(3)
        test_name = products[0].product_name + products[1].product_name + products[2].product_name
        resp = self.app.get(
            BASE_URL, query_string="name={}".format(quote_plus(test_name))
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 0)
    
    def test_query_product_list_by_condition(self):
        """Query Products by condition"""
        products = self._create_products(10)
        test_condition = products[0].condition.name
        condition_products = [product for product in products if product.condition.name == test_condition]
        resp = self.app.get(
            BASE_URL, query_string="condition={}".format(quote_plus(test_condition))
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(condition_products))
        # check the data just to be sure
        for product in data:
            self.assertEqual(product["condition"], test_condition)
    def test_query_products_with_not_exist_condition(self):
        """Query Products by non-exist condition"""
        products = self._create_products(3)
        test_condition = "NEWOLD"
        try:
            resp = self.app.get(
                BASE_URL, query_string="condition={}".format(quote_plus(test_condition))
            )
        except:
            print("successful")
            return
        self.assertFalse(True)
    
    def test_get_product_not_found(self):
        """Get a Product thats not found"""
        resp = self.app.get("/products/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_product(self):
        """Create a new Product"""
        test_product = ProductFactory()
        logging.debug(test_product)
        resp = self.app.post(
            BASE_URL, json=test_product.serialize(), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)
        # Check the data is correct
        new_product = resp.get_json()
        self.assertEqual(new_product["name"], test_product.product_name, "Names do not match")
        self.assertEqual(
            new_product["quantity"], test_product.quantity, "Quantity do not match"
        )
        # Check that the location header was correct
        print(location)
        resp = self.app.get(location, content_type=CONTENT_TYPE_JSON)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_product = resp.get_json()
        self.assertEqual(new_product["name"], test_product.product_name, "Names do not match")
        self.assertEqual(
            new_product["quantity"], test_product.quantity, "Quantity do not match"
        )

    def test_create_existing_product(self):
        """Create an existing Product"""
        # create an product to update
        test_product = ProductFactory()
        resp = self.app.post( # Create the product
            BASE_URL, json=test_product.serialize(), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        
        # update the product
        new_product = resp.get_json()

        resp = self.app.post(
            BASE_URL, json=new_product, content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)

    def test_create_product_no_data(self):
        """Create a Product with missing data"""
        resp = self.app.post(BASE_URL, json={}, content_type=CONTENT_TYPE_JSON)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_product_no_content_type(self):
        """Create a Product with no content type"""
        resp = self.app.post(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_update_product(self):
        """Update an existing Product"""
        # create an product to update
        test_product = ProductFactory()
        resp = self.app.post( # Create the product
            BASE_URL, json=test_product.serialize(), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # update the product
        new_product = resp.get_json()
        print(new_product)
        logging.debug(new_product)
        new_product["quantity"] = 50
        resp = self.app.put(
            BASE_URL + "/{}/condition/{}".format(new_product["product_id"], new_product["condition"]),
            json=new_product,
            content_type=CONTENT_TYPE_JSON,
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_product = resp.get_json()
        self.assertEqual(new_product["id"], updated_product["id"])
        self.assertEqual(new_product["quantity"], updated_product["quantity"])
        self.assertEqual(new_product["condition"], updated_product["condition"])

    def test_update_product_not_found(self):
        """Update a non-existing Product"""
        # create an product without id to update
        new_product = ProductFactory()
        resp = self.app.put(
            BASE_URL + "/{}/condition/{}".format(new_product.product_id, new_product.condition.name),
            json=new_product.serialize(),
            content_type=CONTENT_TYPE_JSON,
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_product(self):
        """Delete a Product"""
        test_product = self._create_products(1)[0]
        resp = self.app.delete(
            "{0}/{1}/condition/{2}".format(BASE_URL, test_product.product_id, test_product.condition.name), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        # make sure they are deleted
        # resp = self.app.get(
        #     "{0}/{1}".format(BASE_URL, test_product.id), content_type=CONTENT_TYPE_JSON
        # )
        # self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_method_not_allowed(self):
        resp = self.app.put(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    
