import os
import csv
import types


class DataLoader:
    """
    This class is meant to load CSV data from a directory and returning a stream
    (one `yield` per file) of stream (one yield per line) of dictionnaries
    (keys are CSV headers)
    """
    _casts = {}

    @staticmethod
    def add_cast(field, what):
        if isinstance(field, types.ListType):
            for f in field:
                DataLoader.add_cast(f, what)
            return
        if what not in DataLoader._casts.keys():
            DataLoader._casts[what] = []
        DataLoader._casts[what].append(field)


    def __init__(self):
        self._data_file_extension = "csv"

    def extract_from_dir(self, dir_path):
        for file_path in self.list_data_files(dir_path):
            file_data = self.extract_from_file(file_path)
            yield file_data

    def extract_from_file(self, file_path):
        reader = csv.reader(open(file_path))
        header = None
        for row in reader:
            if header is None:
                header = row
                continue
            value_point = dict(zip(header, row))
            self._clean_data_value(value_point)
            yield value_point

    def list_data_files(self, dir_path):
        for fileName in os.listdir(dir_path):
            if fileName.endswith("." + self._data_file_extension):
                yield os.path.join(dir_path, fileName)

    def _clean_data_value(self, value_point):
        for wishedType, fields in DataLoader._casts.items():
            for field in fields:
                if field in value_point.keys():
                    casted = self._cast(wishedType, value_point[field])
                    value_point[field] = casted

    def _cast(self, wishedType, value):
        if wishedType == 'int':
            return int(value)
        if wishedType == 'float':
            return float(value)
        if wishedType == 'percentage':
            value = self._cast('float', value)
            return value * 100.0
        return value