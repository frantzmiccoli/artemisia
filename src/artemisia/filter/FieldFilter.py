import types


class FieldFilter:
    """
    This class is supposed to filter a point, it manages multiple element as input
    FieldFilter('problem_type','Step')
    FieldFilter('problem_type','=','Step')
    FieldFilter('best_fitness','<','1200')

    """

    def __init__(self, *args):
        args = list(args)
        self._target_field = args.pop(0)
        self._filter_func = self._filter_func_from_arg(args.pop(0))
        self._extra_args = args

    def match(self, file_data):
        if isinstance(file_data, types.ListType):
            return self._match_file_data(file_data)
        else:
            return self._match_value_point(file_data)

    def get_target_field(self):
        return self._target_field

    def _match_value_point(self, value_point):
        field_value = self._get_field_value(value_point)

        if field_value is None:
            return False

        filter_args = [field_value] + self._extra_args
        match = self._filter_func(*filter_args)
        return match

    def _match_file_data(self, file_data):
        value_point = file_data[0]
        match = self._match_value_point(value_point)

        if match:
            return True

        # if we have a float this value may be dynamic and we carry on with
        # other item of the file_data
        is_castable_to_float = True
        field_value = self._get_field_value(value_point)
        try:
            float(field_value)
        except (ValueError):
            is_castable_to_float = False

        if not is_castable_to_float:
            return match # which is False here

        remaining_file_data = file_data[1:]
        if len(remaining_file_data) == 0:
            return match # which is False here

        return self._match_file_data(remaining_file_data)

    def _match_value_point(self, value_point):
        field_value = self._get_field_value(value_point)
        filter_args = [field_value] + self._extra_args
        return self._filter_func(*filter_args)

    def _get_field_value(self, value_point):
        keys = value_point.keys()
        if self._target_field in keys:
            return value_point[self._target_field]

        if (self._target_field[0] != '|') | \
            (self._target_field[-1] != '|'):
            return None

        clean_field = self._target_field[1:-1]
        if clean_field not in keys:
            return None

        return abs(value_point[clean_field])

    def _filter_func_from_arg(self, arg):
        if isinstance(arg, types.FunctionType):
            return arg
        if arg == 'not in':
            def filter_func(*args):
                args = list(args)
                value = args.pop(0)
                return not (value in args)
            return filter_func
        if arg == 'in':
            def filter_func(*args):
                args = list(args)
                value = args.pop(0)
                return value in args
            return filter_func
        if arg in ['=', '<', '<=', '>', '>=']:
            def filter_func(value, comparison_value):
                try:
                    value = float(value)
                    comparison_value = float(comparison_value)
                except (ValueError):
                    # We may have strings
                    value = str(value).lower()
                    comparison_value = str(comparison_value).lower()
                if arg == '=':
                    return value == comparison_value
                if arg == '<':
                    return value < comparison_value
                if arg == '<=':
                    return value <= comparison_value
                if arg == '>':
                    return value > comparison_value
                if arg == '>=':
                    return value >= comparison_value
            return filter_func
        if isinstance(arg, types.StringType):
            arg = arg.lower()

            def is_in(value):
                return arg in value.lower()
            return is_in
        raise Exception("Dafuq are you sending as input to this function?")
