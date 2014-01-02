import types
import re
from artemisia.filter.FieldFilter import FieldFilter
import artemisia.helper as ahelper


class FilterManager:
    """
    This class is used as a filter manager. You load filters in it, and gives it
    a generator to get another generator yielding only the filtered elements.
    """

    def __init__(self):
        self._file_data_filters = []
        self._first_to_match_filters = []

        self._filter_re = re.compile('^\s*\(((?:,?(?:[^,]+))+)\)\s*$')

    def add_file_data_filter(self, *args):
        """
        Add a filter that will be use to filter the data

          * field,                string, that should be filtered
          * filter_func, function|string, the function to apply
          * filter_func_extra_arg
          * ...
        """
        if isinstance(args[0], types.StringType) & (len(args) == 1):
            args = self._parse_filter(args[0])
        self._file_data_filters.append(FieldFilter(*args))

    def add_first_to_match_filter(self, *args):
        """
        Add a filter that will be use to pick a value point of the data

          * field,                string, that should be filtered
          * filter_func, function|string, the function to apply
          * filter_func_extra_arg
          * ...
        """
        if args[0] == "last":
            self._first_to_match_filters.append(args[0])
            return
        if isinstance(args[0], types.StringType) & (len(args) == 1):
            args = self._parse_filter(args[0])
        self._first_to_match_filters.append(FieldFilter(*args))

    def filter(self, data_generator):
        """
        Yield filtered value

        The dataGenerator will be iterated, filters let filter entries that
        match the filters
        """
        if self._should_flatten_generator():
            print "flattening"
            data_generator = self._flatten(data_generator)
        print "flat or not flat"
        for file_data in data_generator:
            if isinstance(file_data, types.GeneratorType):
                file_data = [value_point for value_point in file_data]
            if self._data_matches_filters(file_data):
                if self._should_flatten_generator():
                    yield file_data
                else:
                    value_point = self._extract_data_point(file_data)
                    if value_point is None:
                        continue
                    yield value_point

    def get_target_fields(self):
        fields = []
        for single_filter in \
            (self._first_to_match_filters + self._file_data_filters):
            if isinstance(single_filter, FieldFilter):
                fields.append(single_filter.get_target_field())
        return fields

    def _flatten(self, generator):
        """
        if the generator yield dictionaries, this function will yield
        dictionary, if the generator yield arrays, this function yield
        the arrays values.
        """
        helper = ahelper.Helper()
        for v in helper.flatten(generator):
            yield v

    def _data_matches_filters(self, data):
        """
        Check if file_data matches the filters

        Adapt itself to either work with file_data as a dict or a list, the list
        is assume to contain a list of dict
        """
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
                    if len(file_data) == 0:
                        return
                    return file_data[-1]
                if not field_filter.match(value_point):
                    continue
                return value_point

    def _should_flatten_generator(self):
        return len(self._first_to_match_filters) == 0

    def _parse_filter(self, filter_string):
        filter_string = filter_string.strip()
        match = self._filter_re.match(filter_string)
        if match is None:
            filter_elements = filter_string.split(' ')
            return filter_elements
        stripped = match.group(0)[1:-1]
        filter_elements = stripped.split(',')
        return filter_elements