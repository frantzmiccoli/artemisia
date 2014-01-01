import arff
import csv

import artemisia.helper as ahelper


class ExporterFactory:
    def get_exporter_factory(self, export_type):
        export_type = export_type.lower()
        if export_type == 'arff':
            exporter = ArffExporter()
        elif export_type == 'csv':
            exporter = CsvExporter()
        else:
            raise Exception('Unexpected type ' + export_type)
        return exporter


class Exporter:
    def __init__(self):
        self._columns = None
        self._file_path = 'export.arff'
        self._relation_name = 'artemisia_export'

    def _export(self, file_data_generator):
        raise NotImplementedError("Please implement this method in a subclass")

    def export(self, file_data_generator):
        prepared_generator = self._prepare_generator(file_data_generator)
        return self._export(prepared_generator)

    def set_columns(self, columns):
        self._columns = columns

    def set_output_file_path(self, file_path):
        self._file_path = file_path

    def set_relation_name(self, relation_name):
        self._relation_name = relation_name

    def _prepare_generator(self, file_data_generator):
        helper = ahelper.Helper()
        for value_point in helper.flatten(file_data_generator):
            if self._columns is None:
                self._columns = value_point.keys()
            value_point = self._get_cleaned_value_point(value_point)
            yield value_point

    def _get_cleaned_value_point(self, value_point):
        if self._columns is None:
            return value_point
        return {column: value_point[column] for column in self._columns}


class ArffExporter(Exporter):
    def _export(self, file_data_generator):
        value_array_generator = self._get_value_array_generator(
            file_data_generator)
        arff.dump(self._file_path, value_array_generator,
                  relation=self._relation_name, names=self._columns)

    def _get_value_array_generator(self, file_data_generator):
        for value_point in file_data_generator:
            value_array = []
            for column in self._columns:
                value_array.append(value_point[column])
            yield value_array


class CsvExporter(Exporter):
    def _export(self, file_data_generator):
        writer = csv.DictWriter(open(self._file_path, 'w'), self._columns)
        header_line = dict(zip(self._columns, self._columns))
        writer.writerow(header_line)
        for value_point in file_data_generator:
            writer.writerow(value_point)