import unittest

from artemisia.exporter.arff_exporter import ArffExporter


class ArffExporterTest(unittest.TestCase):

    def test_export(self):
        exporter = ArffExporter()
        exporter.set_columns('problem,iteration,weight'.split(','))
        file_data = self._get_fake_file_data()
        exporter.export(file_data)
        output = exporter.get_output()
        assert_done = 0
        for line in output.split("\n"):
            if '@ATTRIBUTE problem' in line:
                message = 'This line should contains something like ' + \
                          '"{tsp_solution, othersolution}"'
                self.assertTrue('tsp_solution' in line, message)
                self.assertTrue('other_solution' in line, message)
                self.assertTrue('{' in line, message)
                self.assertTrue('}' in line, message)
                assert_done += 4

        self.assertEqual(4, assert_done)

        self.assertTrue('@ATTRIBUTE iteration numeric' in output)
        self.assertTrue('@ATTRIBUTE weight numeric' in output)
        self.assertTrue('@ATTRIBUTE width numeric' not in output)

    def _get_fake_file_data(self):
        file_data = [{'problem': 'tsp_solution',
                      'width': 150,
                      'iteration': 213,
                      'weight': -15},
                     {'problem': 'tsp_solution',
                      'width': 153,
                      'iteration': 250,
                      'weight': 14},
                     {'problem': 'other_solution',
                      'width': 15,
                      'iteration': 213,
                      'weight': -15},
                     {'problem': 'other_solution',
                      'width': 12,
                      'iteration': 250,
                      'weight': 11}]
        return file_data