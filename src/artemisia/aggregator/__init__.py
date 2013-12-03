import sqlite3
import os
import re
import types
import numpy


class Aggregator:
    """
    This class is meant to aggregate data, it stores them in a SQL light
    database, and then run a query against them to give analytics like data/
    """

    def __init__(self):
        self._aggregate_columns = []
        self._target_value = 'COUNT(*)'
        self._table_name = 'data_point'

        self._target_value_pattern = '(\w*)\s*\(\s*([\w\*]+)\s*\)'

    def add_aggregate_column(self, column_name):
        """
        Add a dimension to aggregate over

        Expected argument like 'connect_strategy'
        """
        if self._get_target_column(column_name) is not None:
            self.set_target_value(column_name)
            return False
        self._aggregate_columns.append(column_name)

    def set_target_value(self, target_value):
        """
        Set the target value, default is 'COUNT(*)'
        """
        self._target_value = target_value

    def aggregate(self, data_generator = None):
        """
        Aggregate the data as defined in the object
        """
        if data_generator is not None:
            self._init_database()
            self._load_from_generator(data_generator)
            self._connection.commit()
        return self._query_aggregate()

    def aggregate_matrix(self, data_generator):
        """
        Aggregate the data return them in a matrix composed of dict
        """
        aggregate_generator = self.aggregate(data_generator)
        if len(self._aggregate_columns) == 0:
            return aggregate_generator.next['aggregate']
        return self._generator_to_matrix(aggregate_generator,
                                         self._aggregate_columns)


    def _init_database(self):
        self._connection = sqlite3.connect(':memory:')
        self._connection.create_aggregate("STDDEV", 1, StdDevAggregate)

        create_statement = 'CREATE TABLE ' + self._table_name + '''
                            (id INTEGER PRIMARY KEY, '''\
                           + self._get_columns_declaration() + ''')'''

        self._connection.execute(create_statement)

    def _get_columns_declaration(self):
        column_declaration_units = [column_name + ' VARCHAR(50)' for column_name in self._aggregate_columns]
        target_column = self._get_target_column()
        if target_column is not None:
            column_declaration_units.append(target_column + ' FLOAT')
        return ', '.join(column_declaration_units)

    def _load_from_generator(self, data_generator):
        for file_data in data_generator:
            if isinstance(file_data, types.DictionaryType):
                self._load_value_point(file_data)
            elif isinstance(file_data, types.ListType):
                for value_point in file_data:
                    self._load_value_point(value_point)
            else:
                raise "Unexcepted type"

    def _load_value_point(self, value_point):
        columns = self._get_columns()
        # A crash in the line below may mean that one of the column doesn't
        # exist in the value point
        values = ['\'' + str(value_point[column]) + '\'' for column in columns]
        insert_statement = 'INSERT INTO ' + self._table_name + ' (id, '\
                           + ', '.join(columns)\
                           + ') VALUES (null, ' + ', '.join(values) + ')'
        self._connection.execute(insert_statement)

    def _query_aggregate(self):
        columns = self._aggregate_columns[:]
        queried_columns = columns + [self._target_value]
        aggregate_statement = 'SELECT ' + ', '.join(queried_columns)\
                                    + ' FROM ' + self._table_name
        if len(columns) != 0:
            aggregate_statement += ' GROUP BY ' + ', '.join(columns)

        cursor = self._connection.cursor()
        cursor.execute(aggregate_statement)
        keys = columns + ['aggregate']
        for aggregate_data_line in cursor:
            def try_float(x):
                try:
                    return float(x)
                except ValueError:
                    return x
            aggregate_data_line = map(try_float, aggregate_data_line)
            aggregate_data_dict = dict(zip(keys, aggregate_data_line))
            # we duplicate the value, that will ease the parsing
            aggregate_data_dict[self._target_value] = \
                aggregate_data_dict['aggregate']
            yield aggregate_data_dict

    def _get_columns(self):
        columns = self._aggregate_columns[:]
        target_column = self._get_target_column()
        if target_column is not None:
            columns.append(target_column)
        return columns

    def _get_target_column(self, target_value_string=None):
        if target_value_string is None:
            target_value_string = self._target_value
        result = re.search(self._target_value_pattern,
                           target_value_string)
        if result is None:
            return None
        groups = result.groups()
        target_column = groups[1]
        if target_column == '*':
            return None
        return target_column

    def _generator_to_matrix(self, generator, columns):
        aggregate_matrix = {}
        for aggregate_value_point in generator:
            current_dict = aggregate_matrix
            for column in columns:
                column_value = aggregate_value_point[column]
                if column_value not in current_dict.keys():
                    current_dict[column_value] = {}
                if column == columns[-1]:
                    current_dict[column_value] = \
                        aggregate_value_point['aggregate']
                current_dict = current_dict[column_value]
        return aggregate_matrix



class StdDevAggregate:
    def __init__(self):
        self.values = []

    def step(self, value):
        self.values.append(value)

    def finalize(self):
        return numpy.std(self.values)