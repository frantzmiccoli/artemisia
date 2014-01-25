import unittest
from filter_test import FilterTest
from aggregator_test import AggregatorTest
from modifier_test import ModifierTest
from arff_exporter_test import ArffExporterTest

if __name__ == '__main__':
    suite = unittest.TestSuite()
    test_cases = [FilterTest,
                  AggregatorTest,
                  ModifierTest,
                  ArffExporterTest]
    for case in test_cases:
        suite.addTests(unittest.makeSuite(case))
    unittest.TextTestRunner().run(suite)