import unittest
from app.core.domain.entities.unique_id import UniqueId


class UniqueIdTestCases(unittest.TestCase):

    def test_unique_ids_are_always_generated(self):
        """Test that unique IDs are always generated"""
        id1 = UniqueId()
        id2 = UniqueId()
        self.assertNotEqual(id1.value, id2.value)

    def test_unique_ids_can_be_generated_from_next_id(self):
        """Test that unique IDs are always generated using the next_id() function"""
        _id = UniqueId.next_id()
        self.assertIsNotNone(_id)

    def test_unique_ids_can_be_generated_from_next_id_with_token(self):
        """Test that unique IDs are always generated using the next_id() function with a token"""
        _id = UniqueId.next_id(token="abcdef")
        self.assertIsNotNone(_id)

    def test_unique_ids_can_be_generated_from_next_id_with_token_and_size(self):
        """Test that unique IDs are always generated using the next_id() function with a token and size"""
        _id = UniqueId.next_id(token="abcdef", size=5)
        self.assertIsNotNone(_id)
        self.assertEqual(len(_id), 5)

    def test_2_unique_ids_can_be_generated_from_next_id(self):
        """Test that 2 unique IDs are always generated using the next_id()"""
        _id1 = UniqueId.next_id()
        _id2 = UniqueId.next_id()
        self.assertIsNotNone(_id1)
        self.assertIsNotNone(_id2)
        self.assertNotEqual(_id1, _id2)


if __name__ == "__main__":
    unittest.main()
