from artemisia.exporter.abstract_exporter import Exporter
import itertools


class ArffExporter(Exporter):

    def __init__(self):
        Exporter.__init__(self)

        self._arff_max_fetched_values = 30
        self._arff_max_class_value = 10
        self._arff_fetched_values = {}
        self._arff_guessed_types = {}

    def _export(self, file_data_generator):
        (generator1, generator2) = itertools.tee(file_data_generator, 2)
        self._guess_types(generator1)

        f = open(self._file_path, 'w')
        f.write(self._get_arff_header())

        first = True
        for value_point in generator2:
            if first:
                f.write("\n")
            else:
                first = False
            f.write(self._get_arff_row_value_point(value_point))

    def _get_value_array_generator(self, file_data_generator):
        for value_point in file_data_generator:
            value_array = []
            for column in self._columns:
                value_array.append(value_point[column])
            yield value_array

    def _guess_types(self, file_data_generator):
        self._load_fetched_values(file_data_generator)
        self._compute_types()

    def _load_fetched_values(self, file_data_generator):
        done = False
        for value_point in file_data_generator:
            if not done:
                done = self._register_fetched_value(value_point)

    def _register_fetched_value(self, value_point):
        done = True
        for (key, value) in value_point.items():
            if key not in self._arff_fetched_values.keys():
                self._arff_fetched_values[key] = []
            if value in self._arff_fetched_values[key]:
                continue
            self._arff_fetched_values[key].append(value)
            if len(self._arff_fetched_values[key]) \
                    < self._arff_max_fetched_values:
                done = False
        return done

    def _compute_types(self):
        for key in self._arff_fetched_values.viewkeys():
            self._compute_type_for_key(key)

    def _compute_type_for_key(self, key):
        values = self._arff_fetched_values[key]
        value_type = None
        for value in values:
            current_value_type = self._guess_value_type(value)
            if value_type is None:
                value_type = current_value_type
                continue
            if value_type != current_value_type:
                if current_value_type == 'string':
                    value_type = current_value_type
        if (value_type == 'string') \
                & (len(values) <= self._arff_max_class_value):
            value_type = '{' + ','.join(values) + '}'
        self._arff_guessed_types[key] = value_type
        return value_type

    def _guess_value_type(self, value):
        try:
            value = float(value)
            castable_as_float = True
            try:
                castable_as_int = (value == int(value))
            except ValueError:
                castable_as_int = False
        except ValueError:
            castable_as_float = False
            castable_as_int = False
        if castable_as_int:
            return 'numeric'
        if castable_as_float:
            return 'numeric'
        return 'string'

    def _get_arff_header(self):
        s = '@RELATION ' + self._relation_name + "\n"
        for (key, value_type) in self._arff_guessed_types.items():
            s += '@ATTRIBUTE ' + key + ' ' + value_type + "\n"
        s += "@DATA" + "\n"
        return s

    def _get_arff_row_value_point(self, value_point):
        values = []
        for key in self._arff_guessed_types.viewkeys():
            values.append(str(value_point[key]))
        return ','.join(values)


