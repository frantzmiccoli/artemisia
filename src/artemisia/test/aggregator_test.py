import unittest
import artemisia.aggregator as aggregator


class AggregatorTest(unittest.TestCase):

    def test_aggregator_count_single_dimension(self):
        agg = aggregator.Aggregator()
        agg.add_aggregate_column('seller')
        per_seller_aggregate = agg.aggregate(self._get_test_data())
        per_seller = {value['seller']: value['aggregate']
                      for value in per_seller_aggregate}
        self.assertIn('amazon', per_seller.keys())
        self.assertIn('bestbuy', per_seller.keys())
        self.assertIn('apple', per_seller.keys())
        self.assertEqual(5, per_seller['amazon'])
        self.assertEqual(2, per_seller['apple'])
        self.assertEqual(1, per_seller['bestbuy'])

    def test_global_avg(self):
        agg = aggregator.Aggregator()
        agg.set_target_value('AVG(price)')
        avg_aggregate = agg.aggregate(self._get_test_data())
        avg = avg_aggregate.next()['aggregate']
        expected_avg = 78.80
        self.assertEqual(round(expected_avg), round(avg))

    def test_min_multiple_dimension(self):
        agg = aggregator.Aggregator()
        agg.set_target_value('MIN(price)')
        agg.add_aggregate_column('category')
        agg.add_aggregate_column('color')
        aggregated_matrix = agg.aggregate_matrix(self._get_test_data())
        self.assertTrue(aggregated_matrix.has_key('book'))
        self.assertEqual(12.4, aggregated_matrix['book']['red'])
        self.assertEqual(0.79, aggregated_matrix['it']['red'])

    def _get_test_data(self):
        return [
            {'seller': 'amazon', 'category': 'book', 'color': 'blue',
             'price': 12},
            {'seller': 'amazon', 'category': 'book', 'color': 'red',
             'price': 12.4},
            {'seller': 'amazon', 'category': 'kitchen', 'color': 'red',
             'price': 12},
            {'seller': 'amazon', 'category': 'book', 'color': 'blue',
             'price': 12.23},
            {'seller': 'bestbuy', 'category': 'it', 'color': 'green',
             'price': 1},
            {'seller': 'amazon', 'category': 'it', 'color': 'red',
             'price': 21},
            # data heterogeneity shouldn't appear in real conditions, here we mix
            # dict and list of dict to test in deep
            [{'seller': 'apple', 'category': 'it', 'color': 'red',
              'price': 559},
            {'seller': 'apple', 'category': 'it', 'color': 'red',
             'price': 0.79}]
        ]