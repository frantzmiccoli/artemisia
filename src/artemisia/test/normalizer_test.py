import unittest
import galimpico.modifier.normalizer as gnormalizer

class NormalizerTest(unittest.TestCase):

    def test_gnormalizer(self):
        test_data = self._get_test_data()
        normalizer = gnormalizer.Normalizer(None)
        normalizer._compute_normalization_data(test_data, "testhash")


        to_normalize_data = {'problem_type': 'tsp',
                            'best_fitness': 11}
        output_point = normalizer.normalize(to_normalize_data)
        normalized_best_fitness = output_point['normalized_best_fitness']
        self.assertEqual(-6, round(normalized_best_fitness))

        to_normalize_data = {'problem_type': 'test',
                             'best_fitness': 1.5}
        output_point = normalizer.normalize(to_normalize_data)
        normalized_best_fitness = output_point['normalized_best_fitness']
        self.assertEqual(1, round(normalized_best_fitness))

    def _get_test_data(self):
        return [
            {'problem_type': 'tsp', 'best_fitness': 12.1},
            {'problem_type': 'tsp', 'best_fitness': 12.2},
            {'problem_type': 'tsp', 'best_fitness': 12.3},
            {'problem_type': 'tsp', 'best_fitness': 12.4},
            {'problem_type': 'tsp', 'best_fitness': 12.5},
            {'problem_type': 'tsp', 'best_fitness': 12.6},
            {'problem_type': 'tsp', 'best_fitness': 12.7},
            {'problem_type': 'tsp', 'best_fitness': 12.8},
            {'problem_type': 'tsp', 'best_fitness': 12.9},
            {'problem_type': 'test', 'best_fitness': 1.9},
            {'problem_type': 'test', 'best_fitness': 1.1},
            {'problem_type': 'test', 'best_fitness': 1.4},
            {'problem_type': 'test', 'best_fitness': 0},
        ]