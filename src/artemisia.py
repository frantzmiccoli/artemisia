import argparse
import re
import sys
import os
import types

import artemisia.dataloader as dataloader
import artemisia.modifier as gmodifier
import artemisia.filter as gfilter
import artemisia.viewer as gviewer
from artemisia import helper as ghelper
import artemisia.modifier.cluster as cluster_modifier
import artemisia.modifier.normalizer as normalizer_modifier
import artemisia.registry as registry

class Artemisia:

    def __init__(self):
        self._filter_re = re.compile('^\s*\(((?:,?(?:[^,]+))+)\)\s*$')
        self._modifier_modules = [cluster_modifier, normalizer_modifier]

    def configure(self):
        self._parse_args()
        self._value_point_filters = self._get_value_points_filters()
        self._first_to_match_filters = self._get_first_to_match_filters()
        self._modifiers = self._get_modifiers()

    def run(self):
        loader = dataloader.DataLoader()
        file_data_generator = loader.extract_from_path(self.get_data_dir_path())

        modifier_manager = gmodifier.ModifierManager()
        [modifier_manager.add_modifier(modifier)
            for modifier in self._modifiers]
        modified_generator = modifier_manager.run(file_data_generator)

        filter_manager = gfilter.FilterManager()
        [filter_manager.add_file_data_filter(*single_filter)
            for single_filter in self._value_point_filters]
        [filter_manager.add_first_to_match_filter(*single_filter)
            for single_filter in self._first_to_match_filters]

        final_data_generator = filter_manager.filter(modified_generator)

        v = gviewer.Viewer()
        v.plot(final_data_generator, self._args.x, self._args.y,
               color_column=self._args.color, scatter=self._args.scatter,
               output_file_name=self._args.output)

    def get_data_dir_path(self):
        return self._args.input

    def _parse_args(self):
        description = '''
        Artemisia tool is meant to parse data in CSV to build graph after some
        basic preprocessing
        '''
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument("-x", action="store", dest="x",
                            help="The data field to use for the x side of "
                                 "the plot")
        parser.add_argument("-y", action="store", dest="y", default=None,
                            help="The data field to use for the y side of "
                                 "the plot")
        parser.add_argument("-c", action="store", dest="color", default=None,
                            help="The data field to use for coloring elements "
                                 "of the plot")
        parser.add_argument("-m", action="append", dest="matches", default=[],
                            help="Consider the first element of a simulation "
                                 "data that match this filter")
        parser.add_argument("-f", action="append", dest="filters", default=[],
                            help="Consider only elements that match this"
                                 " filter")
        parser.add_argument("-l", action="store", dest="loader", default=None,
                            help="A python package to use as loader")
        parser.add_argument("-s", action="store_true", dest="scatter",
                            default=False, help="Flag to force scatter plot")
        parser.add_argument("-i", action="store", dest="input", default='./',
                            help="The input dir to consider (mandatory)")
        parser.add_argument("-o", action="store", dest="output",
                            default="out.png",
                            help="The output file to use")

        self._args = parser.parse_args()

    def _get_value_points_filters(self):
        return self._get_filters_from_arg_string(self._args.filters)

    def _get_first_to_match_filters(self):
        return self._get_filters_from_arg_string(self._args.matches)

    def _get_filters_from_arg_string(self, arg_string):
        filters_arg = arg_string
        filters = [self._parse_filter(filter_string)
                   for filter_string in filters_arg]
        return filters

    def _get_modifiers(self):
        if self._args.loader is not None:
            if self._args.loader not in self._modifier_modules:
                self._modifier_modules.append(self._args.loader)

        modifiers_map = {}

        for modifier_module in self._modifier_modules:
            modifiers_map.update(
                self._get_modifiers_map_from_module(modifier_module))

        return self._get_ordered_modifiers(modifiers_map)

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

    def _get_modifiers_map_from_module(self, module):
        if isinstance(module, types.StringType):
            module = self._get_loader_module(module)
        if module is None:
            return []
        columns = self._get_columns()
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
            for (loader_function_pattern, get_modifier)\
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

    def _get_columns(self):
        columns = [single_filter[0]
                   for single_filter in self._value_point_filters]
        columns += [single_filter[0]
                    for single_filter in self._first_to_match_filters]
        columns += [self._args.x]
        if self._args.y is not None:
            columns += [self._args.y]
        if self._args.color is not None:
            columns.append(self._args.color)
        return ghelper.Helper().clean_columns(columns)

    def _parse_filter(self, filter_string):
        filter_string = filter_string.strip()
        match = self._filter_re.match(filter_string)
        if match is None:
            filter_elements = filter_string.split(' ')
            return filter_elements
        stripped = match.group(0)[1:-1]
        filter_elements = stripped.split(',')
        return filter_elements


registry.instance = None

if __name__ == '__main__':
    registry.instance = Artemisia()
    registry.instance.configure()
    registry.instance.run()
