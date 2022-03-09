"""
Models for Product

All of the models are stored in this module
"""
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from enum import Enum

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()

def init_db(app):
    Product.init_db(app)

class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """

    pass


class Condition(Enum):
    """Enumeration of valid Pet Genders"""

    NEW = 0
    OPEN_BOX = 1
    USED = 2
    UNKNOWN = 3


class Product(db.Model):
    """
    Class that represents a Product
    """
    __tablename__ = "products"
    __table_args__ = (
        db.UniqueConstraint('product_name', 'status', name='unique_product_status'),
    )
    # Table Schema
    

    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(128), unique=False, nullable=False)
    quantity = db.Column(db.Integer, default=0)
    # status = db.Column(db.Integer, default=Condition(0)) 
    status = db.Column(db.Enum(Condition), nullable=False, server_default=(Condition.UNKNOWN.name)) 
    def read_csv(self, file_path):
        """
        read data from csv to db table
        """
        df = pd.read_csv(file_path)
        self.id = None
        for _, row in df.iterrows():
            db.session.add(Product(product_name = str(row[1]), quantity =int(row[2]), status=int(row[3])))
            db.session.commit()
        logger.info("loading data from csv file successfully")


    def __repr__(self):
        return "<Product %r id=[%s]>" % (self.product_name, self.id)

    
        

    def create(self):
        """
        Creates a Product to the database
        """
        logger.info("Creating %s with quantity %d", self.product_name, self.quantity)
        self.id = None  # id must be none to generate next primary key
        db.session.add(self)
        db.session.commit()

    def save(self):
        """
        Updates a Product to the database
        """
        logger.info("Saving %s", self.product_name)
        if not self.id:
            raise DataValidationError("Empty ID")
        db.session.commit()

    def delete(self):
        """ Removes a Product from the data store """
        logger.info("Deleting %s", self.product_name)
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """ Serializes a Product into a dictionary """
        return {"id": self.id, "name": self.product_name, "quantity":self.quantity}

    def deserialize(self, data):
        """
        Deserializes a Product from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.product_name = data["product_name"]
            self.quantity = data["quantity"]
        except KeyError as error:
            raise DataValidationError(
                "Invalid Product: missing " + error.args[0]
            )
        except TypeError as error:
            raise DataValidationError(
                "Invalid Product: body of request contained bad or no data " + str(error)
            )
        return self

    @classmethod
    def init_db(cls, app: Flask):
        """ Initializes the database session """
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables
        # first time init need this
        # Product.read_csv(app,"./products.csv")
        #q1 = db.session.query(Product).filter(Product.product_name=="apple").first()
        #q2 = db.session.query(Product).filter(Product.id==1).first()
        #print(q1)
        #print(q2)
        

    @classmethod
    def all(cls):
        """ Returns all of the Products in the database """
        logger.info("Processing all Products")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """ Finds a Product by it's ID """
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)

    @classmethod
    def find_or_404(cls, by_id):
        """ Find a Product by it's id """
        logger.info("Processing lookup or 404 for id %s ...", by_id)
        return cls.query.get_or_404(by_id)

    @classmethod
    def find_by_name(cls, name):
        """Returns all Products with the given name

        Args:
            name (string): the name of the Products you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.product_name == name)
