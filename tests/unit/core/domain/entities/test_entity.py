import unittest
import pytest
from app.core.domain.entities.entity import Entity


@pytest.mark.unit
class EntityTestCases(unittest.TestCase):
    def test_new_entity_has_unique_id(self):
        """Test a new Entity always has an ID"""
        entity = Entity()
        self.assertIsNotNone(entity.id)

    def test_new_entities_always_have_unique_ids(self):
        """Test new Entities always have unique IDs"""
        entity_one = Entity()
        entity_two = Entity()

        self.assertIsNotNone(entity_one.id)
        self.assertIsNotNone(entity_two.id)
        self.assertNotEqual(entity_one.id, entity_two.id)


if __name__ == '__main__':
    unittest.main()
