from artemisia.exporter.abstract_exporter import Exporter
import csv


class CsvExporter(Exporter):

    def _export(self, file_data_generator):
        f = self.get_file_handle()
        writer = csv.DictWriter(f, self._columns)
        header_line = dict(zip(self._columns, self._columns))
        writer.writerow(header_line)
        for value_point in file_data_generator:
            writer.writerow(value_point)