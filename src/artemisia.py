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
import artemisia.registry as registry

class Artemisia:

    def __init__(self):
        pass

    def configure(self):
        self._parse_args()
        self._value_point_filters = self._get_value_points_filters()
        self._first_to_match_filters = self._get_first_to_match_filters()

    def run(self):
        loader = dataloader.DataLoader()
        file_data_generator = loader.extract_from_path(self.get_data_dir_path())

        modifier_manager = gmodifier.ModifierManager()
        modifier_manager.add_lookup_module(self._args.loader)
        modifier_manager.load_modifiers_from_columns(self._get_columns())
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



registry.instance = None

if __name__ == '__main__':
    registry.instance = Artemisia()
    registry.instance.configure()
    registry.instance.run()
