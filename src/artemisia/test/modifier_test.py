import unittest

from artemisia.modifier import ModifierManager
import artemisia.modifier.cluster as acluster


class ModifierTest(unittest.TestCase):

    def test_modifier_manager(self):
        file_data = self._get_fake_file_data()

        modifier_manager = ModifierManager()

        modifier_manager.add_lookup_module('artemisia.test.dummy_package')
        modifier_manager.add_lookup_module(acluster)

        columns = ['width_cluster_2', 'size']
        modifier_manager.load_modifiers_from_columns(columns)
        modified_file_generator = modifier_manager.run(file_data)
        for value_point in modified_file_generator:
            width_cluster = value_point['width_cluster_2']
            self.assertEqual(0, width_cluster, 'This one cluster should be 0')

            size = value_point['size']
            self.assertEqual(12, size, 'Size is hardcoded to 12')

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