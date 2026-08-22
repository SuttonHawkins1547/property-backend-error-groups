import unittest

from property_errors import PropertyEvent, error_group


class PropertyGroupingTest(unittest.TestCase):
    def test_same_property_kind_groups_different_records_together(self):
        first = PropertyEvent("building-17", "inspection", "reminder-204")
        second = PropertyEvent("building-17", "inspection", "reminder-205")
        third = PropertyEvent("building-17", "maintenance", "request-88")

        self.assertEqual(error_group(first), error_group(second))
        self.assertNotEqual(error_group(first), error_group(third))
