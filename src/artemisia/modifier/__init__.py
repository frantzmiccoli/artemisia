import types


class Modifier:
    """
    A modifier is used to alter value_points contains within a generator
    """

    def __init__(self, func):
        self._func = func

    def run(self, data_generator):
        for value_point in data_generator:
            if isinstance(value_point, types.GeneratorType):
                value_point = [d for d in value_point]
            if isinstance(value_point, types.ListType):
                modified_value_point = []
                for value_point_dict in value_point:
                    modified_value_point_dict = self._func(value_point_dict)
                    if modified_value_point_dict is not None:
                        modified_value_point.append(modified_value_point_dict)
                yield modified_value_point
            else:
                modified_value_point = self._func(value_point)
                if modified_value_point is not None:
                    yield modified_value_point


class ModifierManager:
    """
    The ModifierManager apply a set of modifier on a generator
    """
    def __init__(self):
        self._modifiers = []

    def add_modifier(self, func):
        self._modifiers.append(Modifier(func))

    def run(self, data_generator):
        current_generator = data_generator
        for modifier in self._modifiers:
            current_generator = modifier.run(current_generator)
        return current_generator

