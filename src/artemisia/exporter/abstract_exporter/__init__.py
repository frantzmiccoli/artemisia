from StringIO import StringIO
import artemisia.helper as ahelper

class Exporter:
    def __init__(self):
        self._columns = None
        self._file_path = None
        self._file_handle = None
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

    def set_file_handle(self, file_handle):
        self._file_handle = file_handle

    def get_file_handle(self):
        if self._file_handle is None:
            if self._file_path is not None:
                self._file_handle = open(self._file_path, 'w')
            else:
                self._file_handle = StringIO()
        return self._file_handle

    def get_output(self):
        """
        Return the content written by the exporter
        """
        if self._file_handle is None:
            return None
        self._file_handle.seek(0)
        return self._file_handle.read()


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