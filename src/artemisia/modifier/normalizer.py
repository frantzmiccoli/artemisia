import os
import pickle
import hashlib
import re

import artemisia.aggregator as gaggregator
import artemisia.dataloader as gdataloader
import artemisia.filter as gfilter
import artemisia.registry as registry


class Normalizer:

    def __init__(self, data_dir_path, field_to_normalize,
                 fixed_fields=None,
                 normalized_field_prefix='normalized_'):
        self._fixed_fields = fixed_fields or []
        self._field_to_normalize = field_to_normalize
        self._normalized_field_prefix = normalized_field_prefix

        self.filter_manager = gfilter.FilterManager()

        self._data_dir_path = data_dir_path
        self._normalization_data_path_pattern = '/tmp/normalization-%s.data'
        self._data_loader = gdataloader.DataLoader()
        self._normalization_data = None

    def normalize(self, value_point):
        normalization_data = self._get_normalization_data()

        value_point_key = self._get_value_point_key(value_point)
        if value_point_key not in normalization_data.keys():
            raise Exception("Unknown problem type")
        problem_normalization_data = normalization_data[value_point_key]
        # With heterogeneous data the field may not be available
        if self._field_to_normalize in value_point.keys():
            return
        normalized_value = value_point[self._field_to_normalize]

        avg_key = 'AVG(' + self._field_to_normalize + ')'
        normalized_value -= problem_normalization_data[avg_key]
        stddev_key = 'STDDEV(' + self._field_to_normalize + ')'
        normalized_value /= problem_normalization_data[stddev_key]
        normalized_field = self._normalized_field_prefix \
            + self._field_to_normalize
        value_point[normalized_field] = normalized_value
        return value_point

    def _get_value_point_key(self, value_point):
        key_elements = [field + '-->' + str(value_point[field])
                        for field in self._fixed_fields]
        key = '|'.join(key_elements)
        return key

    def _get_data_hash(self):
        file_names_generator = self._data_loader.list_data_files(
            self._data_dir_path)
        data_files = [f for f in file_names_generator]
        data_files_string = ' '.join(data_files)
        file_list_hash = hashlib.md5(data_files_string).hexdigest()
        return file_list_hash

    def _get_normalization_data(self):
        if self._normalization_data is not None:
            return self._normalization_data
        data = None
        if os.path.exists(self._get_normalization_data_path()):
            data = pickle.load(open(self._get_normalization_data_path()))
            expected_hash = self._get_data_hash()
            if expected_hash != data['hash']:
                # hash do not match, data has changed since last computation
                data = None
        if data is None:
            filtered_data = self._get_filtered_data()
            files_hash = self._get_data_hash()
            data = self._compute_normalization_data(filtered_data, files_hash)
        self._normalization_data = data
        self._persist_normalization_data()
        return data

    def _compute_normalization_data(self, filtered_data, files_hash):
        aggregator = gaggregator.Aggregator()
        for field in self._fixed_fields:
            aggregator.add_aggregate_column(field)
        relevant_values = ['MIN(' + self._field_to_normalize + ')',
                           'MAX(' + self._field_to_normalize + ')',
                           'AVG(' + self._field_to_normalize + ')',
                           'STDDEV(' + self._field_to_normalize + ')']
        self._normalization_data = {'hash': files_hash}
        data_pushed = False
        for relevant_value in relevant_values:
            aggregator.set_target_value(relevant_value)
            if not data_pushed:
                aggregated_data = aggregator.aggregate(filtered_data)
                data_pushed = True
            else:
                aggregated_data = aggregator.aggregate()
            self._enrich_normalization_data(relevant_value,
                                            aggregated_data)
        return self._normalization_data

    def _get_filtered_data(self):
        raw = self._data_loader.extract_from_dir(self._data_dir_path)

        filtered_data = self.filter_manager.filter(raw)
        return filtered_data

    def _enrich_normalization_data(self,
                                   relevant_value,
                                   aggregated_data):
        for value_point in aggregated_data:
            value_point_key = self._get_value_point_key(value_point)
            aggregate = value_point['aggregate']
            if value_point_key not in self._normalization_data.keys():
                self._normalization_data[value_point_key] = {}
            self._normalization_data[value_point_key][relevant_value] =\
                aggregate

    def _persist_normalization_data(self):
        if os.path.exists(self._get_normalization_data_path()):
            os.remove(self._get_normalization_data_path())
        pickle.dump(self._normalization_data,
                    open(self._get_normalization_data_path(), 'wb'))

    def _get_normalization_data_path(self):
        hash_input = self._field_to_normalize + '('\
            + ','.join(self._fixed_fields) + ')'
        md5 = hashlib.md5()
        md5.update(hash_input)
        hash_value = md5.hexdigest()
        return self._normalization_data_path_pattern % hash_value


normalized_field_pattern = re.compile('^normalized_([\w\d_]*)$')


def get_normalized_field_modifier(name):
    match = normalized_field_pattern.match(name)
    if match is None:
        raise Exception("Field name is supposed to match the normalized field "
                        "pattern")
    field = match.group(1)
    data_dir_path = registry.instance.get_data_dir_path()
    normalizer = Normalizer(data_dir_path, field)

    def normalized_field_modifier(value_point):
        value_point = normalizer.normalize(value_point)
        return value_point

    return normalized_field_modifier

modifiers_map = {
    normalized_field_pattern: get_normalized_field_modifier
}
