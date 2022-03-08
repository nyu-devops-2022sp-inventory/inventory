"""
Test cases for Product Model

"""
import logging
from multiprocessing import Condition
import unittest
import os
from service.models import Product, DataValidationError, db, Condition
from service import app
from werkzeug.exceptions import NotFound

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

    def test_find_by_name(self):
        """Find a Product by Name"""
        test_product = Product(product_name="Red Apple", quantity=2, status=Condition.NEW)
        test_product.create()
        Product(product_name="Green Apple", quantity=5, status=Condition.OPEN_BOX.name).create()
        products = Product.find_by_name("Red Apple")
        self.assertEqual(products[0].product_name, "Red Apple")
        self.assertEqual(products[0].quantity, 2)
        self.assertEqual(products[0].status, Condition.NEW)
