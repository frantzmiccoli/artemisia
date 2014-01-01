import types
import sys
import os

import cluster as cluster_modifier
import normalizer as normalizer_modifier

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
        self._lookup_modules = [cluster_modifier, normalizer_modifier]

    def add_modifier(self, func):
        self._modifiers.append(Modifier(func))

    def run(self, data_generator):
        current_generator = data_generator
        for modifier in self._modifiers:
            current_generator = modifier.run(current_generator)
        return current_generator

    def add_lookup_module(self, module):
        if isinstance(module, types.StringType):
            module = self._get_loader_module(module)
        if module is None:
            return
        self._lookup_modules.append(module)

    def load_modifiers_from_columns(self, columns):
        for modifier_func in self._get_modifiers_func_from_columns(columns):
            self.add_modifier(modifier_func)

    def _get_modifiers_func_from_columns(self, columns):
        modifiers_map = {}

        for modifier_module in self._lookup_modules:
            modifiers_map.update(
                self._get_modifiers_map_from_module(columns, modifier_module))

        return self._get_ordered_modifiers(modifiers_map)

    def _get_modifiers_map_from_module(self, columns, module):
        """
        The modifier map
        """
        modifiers_map = {}
        loader_functions = dir(module)
        for column in columns:  # for each column
            get_modifier_name = 'get_' + column + '_modifier'
            if get_modifier_name in loader_functions:
                modifier_generator = getattr(module, get_modifier_name)
                modifiers_map[column] = modifier_generator()
            if not hasattr(module, 'modifiers_map'):
                continue
            module_modifiers_map = getattr(module, 'modifiers_map')
            for (loader_function_pattern, get_modifier) \
                in module_modifiers_map.iteritems():
                match = loader_function_pattern.match(column)
                if match is not None:
                    modifiers_map[column] = get_modifier(column)
        return modifiers_map

    def _get_loader_module(self, module_name):
        sys.path.append(os.getcwd())
        loader_package = module_name
        imported_loader = __import__(loader_package)
        split_package = loader_package.split('.')
        while len(split_package) != 0:
            sub_package = split_package.pop(0)
            if sub_package in dir(imported_loader):
                imported_loader = getattr(imported_loader, sub_package)
        return imported_loader

    def _get_ordered_modifiers(self, modifiers_map):
        """
        Return the modifier ordered in a such way that their computation won't
        enter in any dependency problem.
        """
        modified_columns = modifiers_map.keys()
        modified_columns_sorted = []
        while len(modified_columns) != 0:
            parent_columns = self._get_parent_columns(modified_columns)
            modified_columns = list(set(modified_columns) - set(parent_columns))
            modified_columns_sorted += parent_columns
        modifiers = [modifiers_map[column] for column in modified_columns_sorted]
        return modifiers

    def _get_parent_columns(self, columns):
        """
        Get parent columns from a list of columns. A column is a parent one
        if it's not contained in any other one. Among 'cluster_zone_4', 'zone'
        and 'temperature', the parent columns are 'zone' and 'temperature',
        implicitly we assume that 'cluster_zone_4' need 'zone' to be computed.
        """
        parent_columns = []
        for column in columns:
            found_parent = False
            for parent_candidate_column in columns:
                if column == parent_candidate_column:
                    continue
                if parent_candidate_column in column:
                    found_parent = True
                    break
            if not found_parent:
                parent_columns.append(column)
        return parent_columns
