import unittest
from faker import Faker
from faker.providers import lorem
from app.core.domain.entities.unique_id import UniqueId


fake = Faker()
fake.add_provider(lorem)

class UniqueIdTestCases(unittest.TestCase):
    
    def test_unique_ids_are_always_generated(self):
        id1 = UniqueId()
        id2 = UniqueId()
        self.assertNotEqual(id1.value, id2.value)


if __name__ == "__main__":
    unittest.main()
