import unittest
from lib.artemisia.src.artemisia.filter import FilterManager
from lib.artemisia.src.artemisia.filter import FieldFilter


class FilterTest(unittest.TestCase):

    def test_field_filter(self):
        file_data = self._get_fake_file_data()

        field_filter = FieldFilter('problem', 'solution')
        self.assertTrue(field_filter.match(file_data[-1]))

        field_filter = FieldFilter('problem', '=', 'oooo')
        self.assertFalse(field_filter.match(file_data[-1]))

        field_filter = FieldFilter('problem', '=', 'tsp_solution')
        self.assertTrue(field_filter.match(file_data[-1]))

        field_filter = FieldFilter('width', '<=', 100)
        self.assertFalse(field_filter.match(file_data[-1]))

        field_filter = FieldFilter('width', '>', 100)
        self.assertTrue(field_filter.match(file_data[-1]))

        field_filter = FieldFilter('|weight|', '>', 12)
        self.assertTrue(field_filter.match(file_data[0]))

    def test_filter_manager(self):
        file_data = self._get_fake_file_data()

        filter_manager = FilterManager()
        filter_manager.add_file_data_filter('problem', 'solution')
        filter_manager.add_file_data_filter('width', '>', 100)

        filtered = self._generator_to_list(filter_manager.filter([file_data]))
        self.assertEqual(filtered, [file_data])

        filter_manager.add_first_to_match_filter('iteration', '>=', 250)

        filtered = self._generator_to_list(filter_manager.filter([file_data]))
        self.assertEqual(filtered, [file_data[-1]])

        filter_manager.add_file_data_filter('width', '>', 200)

        filtered = self._generator_to_list(filter_manager.filter([file_data]))
        self.assertEqual(filtered, [])

    def _get_fake_file_data(self):
        file_data = [{'problem': 'tsp_solution',
                      'width': 150,
                      'iteration': 213,
                      'weight': -15},
                     {'problem': 'tsp_solution',
                      'width': 150,
                      'iteration': 250,
                      'weight': 11}]
        return file_data


    def _generator_to_list(self, generator):
        return [v for v in generator]

if __name__ == '__main__':
    unittest.main()
