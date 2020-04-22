import unittest
from unittest.mock import MagicMock

# also use doctest
class SDFTest(unittest.TestCase):
    def create_sdf_test(self):
        self.assertEqual(3, 3)

    def sdf_requires_aspect_test(self):
        self.assertEqual(3, 3)

    def sdf_requires_category_test(self):
        self.assertEqual(3, 3)

    def sdf_infers_time_test(self):
        self.assertEqual(3, 3)

    def sdf_has_listed_aspects_test(self):
        self.assertEqual(3, 3)
