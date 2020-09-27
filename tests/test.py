import sys
import unittest

from ValgrindCI import ValgrindData


class TestNumberOfErrors(unittest.TestCase):
    def test_number_of_errors(self):
        data = ValgrindData()
        data.parse("test.xml")
        self.assertEqual(data.get_num_errors(), 2)


suite = unittest.TestLoader().loadTestsFromTestCase(TestNumberOfErrors)
test_result = unittest.TextTestRunner(verbosity=2).run(suite)
if test_result.failures or test_result.errors:
    sys.exit(-1)
