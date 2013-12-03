import types
from artemisia.filter import FieldFilter


class FilterManager:

    def __init__(self):
        self._file_data_filters = []
        self._first_to_match_filters = []

    def add_file_data_filter(self, *args):
        '''
        Add a filter that will be use to filter the data

          * field,                string, that should be filtered
          * filter_func, function|string, the function to apply
          * filter_func_extra_arg
          * ...
        '''
        self._file_data_filters.append(FieldFilter(*args))

    def add_first_to_match_filter(self, *args):
        '''
        Add a filter that will be use to pick a value point of the data

          * field,                string, that should be filtered
          * filter_func, function|string, the function to apply
          * filter_func_extra_arg
          * ...
        '''
        if args[0] == "last":
            self._first_to_match_filters.append(args[0])
            return
        self._first_to_match_filters.append(FieldFilter(*args))

    def filter(self, dataGenerator):
        '''
        Yield filtered value

        The dataGenerator will be iterated, filters let filter entries that
        match the filters
        '''
        for file_data in dataGenerator:
            if isinstance(file_data, types.GeneratorType):
                file_data = [value_point for value_point in file_data]
            if self._data_matches_filters(file_data):
                yield self._extract_data_point(file_data)

    def _data_matches_filters(self, data):
        '''
        Check if file_data matches the filters

        Adapt itself to either work with file_data as a dict or a list, the list
        is assume to contain a list of dict
        '''
        if isinstance(data, types.DictionaryType):
            value_point = data
        elif isinstance(data, types.ListType):
            value_point = data[-1]
        else:
            raise Exception("Unexpected file data")
        for field_filter in self._file_data_filters:
            if not field_filter.match(value_point):
                return False
        return True

    def _extract_data_point(self, file_data):
        if not isinstance(file_data, types.ListType):
            raise Exception("Unexpected input type")
        if len(self._first_to_match_filters) == 0:
            return file_data
        for value_point in file_data:
            for field_filter in self._first_to_match_filters:
                if field_filter == "last":
                    return file_data[-1]
                if not field_filter.match(value_point):
                    continue
                return value_point
