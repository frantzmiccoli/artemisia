import artemisia.exporter.arff_exporter
import artemisia.exporter.csv_exporter


class ExporterFactory:
    def get_exporter_factory(self, export_type):
        export_type = export_type.lower()
        if export_type == 'arff':
            exporter = arff_exporter.ArffExporter()
        elif export_type == 'csv':
            exporter = csv_exporter.CsvExporter()
        else:
            raise Exception('Unexpected type ' + export_type)
        return exporter






