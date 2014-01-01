import argparse

import artemisia.dataloader as dataloader
import artemisia.modifier as gmodifier
import artemisia.filter as gfilter
import artemisia.viewer as gviewer
from artemisia import helper as ghelper
import artemisia.registry as registry
import artemisia.exporter as aexporter

class Artemisia:

    def __init__(self):
        pass

    def configure(self):
        self._parse_args()
        self._filter_manager = None
        self._modifier_manager = None

    def run(self):
        preprocessed_data_processor = self._get_preprocessed_data_generator()

        if self._args.subparser_name == 'export':
            export_type = self._args.type
            exporter = aexporter.ExporterFactory().get_exporter_factory(
                export_type)
            exporter.set_columns(self._args.columns)
            exporter.set_output_file_path(self._args.output)
            exporter.export(preprocessed_data_processor)
        elif self._args.subparser_name == 'plot':
            v = gviewer.Viewer()
            v.plot(preprocessed_data_processor, self._args.x, self._args.y,
                   color_column=self._args.color, scatter=self._args.scatter,
                   output_file_name=self._args.output)

    def get_data_dir_path(self):
        return self._args.input

    def _parse_args(self):
        parser = self._get_parser()
        self._args = parser.parse_args()

    def _get_parser(self):
        main_parser = self._get_main_parser()

        subparsers = main_parser.add_subparsers(dest='subparser_name',
                                                help='commands')
        self._add_plot_subparser(subparsers)
        self._add_export_subparser(subparsers)

        return main_parser

    def _get_main_parser(self):
        description = '''
        Artemisia tool is meant to parse data in CSV to build graph after some
        basic preprocessing.
        '''
        parser = argparse.ArgumentParser(description=description)

        return parser

    def _add_plot_subparser(self, subparsers):
        plot_subparser = subparsers.add_parser('plot')
        self._add_generic_arguments(plot_subparser)
        plot_subparser.add_argument("-x", action="store", dest="x",
                            help="The data field to use for the x side of "
                                 "the plot")
        plot_subparser.add_argument("-y", action="store", dest="y", default=None,
                            help="The data field to use for the y side of "
                                 "the plot")
        plot_subparser.add_argument("-c", action="store", dest="color", default=None,
                            help="The data field to use for coloring elements "
                                 "of the plot")
        plot_subparser.add_argument("-s", action="store_true", dest="scatter",
                            default=False, help="Flag to force scatter plot")
        plot_subparser.add_argument("-o", action="store", dest="output",
                            default="out.png",
                            help="The output file to use")

    def _add_export_subparser(self, subparsers):
        export_subparser = subparsers.add_parser('export')
        self._add_generic_arguments(export_subparser)
        export_subparser.add_argument("-c", action="append", dest="columns",
                                      default=None,
                                      help="The data columns to export")
        export_subparser.add_argument("-t", action="store", dest="type",
                                      default='csv',
                                      help="The type to which export "
                                           "(csv / arff)")
        export_subparser.add_argument("-o", action="store", dest="output",
                                      default='export.arff',
                                      help="The file to which exports")

    def _add_generic_arguments(self, parser):
        parser.add_argument("-m", action="append", dest="matches", default=[],
                            help="Consider the first element of a simulation "
                                 "data that match this filter")
        parser.add_argument("-f", action="append", dest="filters", default=[],
                            help="Consider only elements that match this"
                                 " filter")
        parser.add_argument("-l", action="store", dest="loader", default=None,
                            help="A python package to use as loader")
        parser.add_argument("-i", action="store", dest="input", default='./',
                            help="The input dir to consider (mandatory)")

    def _get_configured_modifier_manager(self):
        if self._modifier_manager is not None:
            return self._modifier_manager
        modifier_manager = gmodifier.ModifierManager()
        modifier_manager.add_lookup_module(self._args.loader)
        modifier_manager.load_modifiers_from_columns(self._get_columns())
        self._modifier_manager = modifier_manager
        return modifier_manager

    def _get_configured_filter_manager(self):
        if self._filter_manager is not None:
            return self._filter_manager
        filter_manager = gfilter.FilterManager()
        [filter_manager.add_file_data_filter(*single_filter)
         for single_filter in self._args.filters]
        [filter_manager.add_first_to_match_filter(*single_filter)
         for single_filter in self._args.matches]
        self._filter_manager = filter_manager
        return filter_manager

    def _get_preprocessed_data_generator(self):
        loader = dataloader.DataLoader()
        file_data_generator = loader.extract_from_path(self.get_data_dir_path())

        modified_generator = self._get_configured_modifier_manager() \
            .run(file_data_generator)

        final_data_generator = self._get_configured_filter_manager() \
            .filter(modified_generator)

        return final_data_generator

    def _get_columns(self):
        columns = self._get_configured_filter_manager().get_target_fields()
        columns += self._get_extra_columns()
        return ghelper.Helper().clean_columns(columns)

    def _get_extra_columns(self):
        subparser_name = self._args.subparser_name
        if subparser_name == 'plot':
            return self._get_plot_extra_columns()
        if subparser_name == 'export':
            return self._get_export_extra_columns()

    def _get_plot_extra_columns(self):
        columns = [self._args.x]
        if self._args.y is not None:
            columns += [self._args.y]
        if self._args.color is not None:
            columns.append(self._args.color)
        return columns

    def _get_export_extra_columns(self):
        return self._args.columns or []


if __name__ == '__main__':
    registry.instance = Artemisia()
    registry.instance.configure()
    registry.instance.run()
