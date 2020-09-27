import sys
import unittest

from ValgrindCI import ValgrindData


class TestValgrindCI(unittest.TestCase):
    def test_number_of_errors(self):
        data = ValgrindData()
        data.parse("test.xml")
        self.assertEqual(data.get_num_errors(), 2)

    def test_list_error_kinds(self):
        data = ValgrindData()
        data.parse("test.xml")
        self.assertEqual(
            data.list_error_kinds(), ["UninitCondition", "Leak_DefinitelyLost"]
        )


suite = unittest.TestLoader().loadTestsFromTestCase(TestValgrindCI)
test_result = unittest.TextTestRunner(verbosity=2).run(suite)
if test_result.failures or test_result.errors:
    sys.exit(-1)
