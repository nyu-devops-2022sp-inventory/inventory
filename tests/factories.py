from multiprocessing import Condition
import factory
from factory.fuzzy import FuzzyChoice, FuzzyInteger
from service.models import Product, Condition


class ProductFactory(factory.Factory):
    """Creates fake pets that you don't have to feed"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Product

    id = factory.Sequence(lambda n: n)
    product_id = FuzzyInteger(10000, 20000)
    product_name = factory.Faker("first_name")
    quantity = factory.Sequence(lambda n: n)
    condition = FuzzyChoice(choices=[Condition.UNKNOWN, Condition.NEW, Condition.OPEN_BOX, Condition.USED])
    # status = FuzzyChoice(choices=["UNKNOWN", "NEW", "OPEN_BOX", "USED"])

