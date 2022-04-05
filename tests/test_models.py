"""
Test cases for Product Model

"""
import logging
from multiprocessing import Condition
import unittest
import os

from numpy import product
from service.models import Product, DataValidationError, db, Condition
from service import app
from werkzeug.exceptions import NotFound
from .factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@postgres:5432/testdb"
)

######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
class TestProductModel(unittest.TestCase):
    """ Test Cases for Product Model """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        db.session.close()

    def setUp(self):
        """ This runs before each test """
        db.drop_all()
        db.create_all()

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()
        db.drop_all()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_XXXX(self):
        """ Test something """
        self.assertTrue(True)

    def test_create_a_product(self):
        """Create a product and assert that it exists"""
        product = Product(product_id = 10001, product_name="Green Apple", quantity=5, status=Condition.OPEN_BOX)
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.product_id, 10001)
        self.assertEqual(product.product_name, "Green Apple")
        self.assertEqual(product.condition, Condition.OPEN_BOX)
        product = Product(product_id = 10001, product_name="Green Apple", quantity=5, status=Condition.UNKNOWN)
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.product_id, 10001)
        self.assertEqual(product.product_name, "Green Apple")
        self.assertEqual(product.condition, Condition.UNKNOWN)

    def test_add_a_product(self):
        """Create a Product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = Product(product_id = 10001, product_name="Green Apple", quantity=5, status=Condition.UNKNOWN)
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertEqual(product.id, 1)
        products = Product.all()
        self.assertEqual(len(products), 1)

    def test_update_a_product(self):
        """Update a Product"""
        product = ProductFactory()
        logging.debug(product)
        product.create()
        logging.debug(product)
        self.assertEqual(product.id, 1)
        # Change it an save it
        product.product_id = 10001
        product.product_name = "apple"
        product.quantity = 100
        product.condition = Condition.UNKNOWN
        original_id = product.id
        product.save()
        self.assertEqual(product.id, original_id)
        self.assertEqual(product.product_id, 10001)
        self.assertEqual(product.product_name, "apple")
        self.assertEqual(product.quantity, 100)
        self.assertEqual(product.condition, Condition.UNKNOWN)
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        products = Product.all()
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].id, 1)
        self.assertEqual(product.product_id, 10001)
        self.assertEqual(products[0].product_name, "apple")
        self.assertEqual(products[0].quantity, 100)
        self.assertEqual(products[0].condition, Condition.UNKNOWN)

    def test_update_empty_id(self):
        """Test update a Product without id"""
        test_product = ProductFactory()
        test_product.id = None
        self.assertRaises(DataValidationError, test_product.save)

    def test_delete_a_product(self):
        """Delete a Product"""
        product = ProductFactory()
        product.create()
        self.assertEqual(len(product.all()), 1)
        # delete the product and make sure it isn't in the database
        product.delete()
        self.assertEqual(len(product.all()), 0)

    def test_serialize_a_product(self):
        """Serialize a Product"""
        product = ProductFactory()
        data = product.serialize()
        self.assertNotEqual(data, None)
        self.assertIn("id", data)
        self.assertEqual(data["id"], product.id)
        self.assertIn("product_id", data)
        self.assertEqual(data["product_id"], product.product_id)
        self.assertIn("name", data)
        self.assertEqual(data["name"], product.product_name)
        self.assertIn("quantity", data)
        self.assertEqual(data["quantity"], product.quantity)
        self.assertIn("condition", data)
        self.assertEqual(data["condition"], product.condition.name)

    def test_deserialize_a_product(self):
        """Test deserialization of a Product"""
        data = {
            "id": 1,
            "product_id": 10001,
            "name": "Apple",
            "quantity": 5,
            "condition": "NEW",
        }
        product = Product()
        product.deserialize(data)
        self.assertNotEqual(product, None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.product_id, 10001)
        self.assertEqual(product.product_name, "Apple")
        self.assertEqual(product.quantity, 5)
        self.assertEqual(product.condition, Condition.NEW)


    def test_deserialize_missing_data(self):
        """Test deserialization of a Product with missing data"""
        data = {"id": 7, "name": "Test Apple"}
        product = Product()
        self.assertRaises(DataValidationError, product.deserialize, data)

    def test_deserialize_bad_data(self):
        """Test deserialization of bad data"""
        data = "this is not a dictionary"
        product = Product()
        self.assertRaises(DataValidationError, product.deserialize, data)


    def test_find_or_404_found(self):
        """Find or return 404 found"""
        products = ProductFactory.create_batch(3)
        for product in products:
            product.create()

        product = product.find_or_404(products[1].id)
        self.assertIsNot(product, None)
        self.assertEqual(product.id, products[1].id)
        self.assertEqual(product.product_name, products[1].product_name)
        self.assertEqual(product.quantity, products[1].quantity)

    def test_find_or_404_not_found(self):
        """Find or return 404 NOT found"""
        self.assertRaises(NotFound, Product.find_or_404, 0)
