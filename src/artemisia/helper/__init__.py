import re
import types


class Helper:
    """
    This class provides a helper well suited for the rest of the manipulation
    It's handling column name manipulation
    """

    def __init__(self):
        self._sql_function_re = re.compile('^\s*\w*\s*\((.*)\)\s*$')

    def clean_columns(self, columns, remove_sql=True):
        """
        Clean column names by removing duplicates. this function takes a list
        and return a list
        """
        while None in columns:
            columns.remove(None)

        cleaned_columns = []
        for column in columns:
            if remove_sql:
                match = self._sql_function_re.match(column)
                if match is not None:
                    column = match.group(1)

            cleaned_columns.append(column)

        cleaned_columns = list(set(cleaned_columns))

        return cleaned_columns

    def is_sql_function(self, column):
        """
        Tell whether or not the given column may be corresponding to an SQL
        function (SQL function must be set as target column within the
        aggregator)
        """
        match = self._sql_function_re.match(column)
        return match is not None

    def flatten(self, generator):
        """
        if the generator yield dictionaries, this function will yield
        dictionary, if the generator yield arrays, this function yield
        the arrays values.
        """
        for item in generator:
            if isinstance(item, types.DictType):
                yield item
            else:
                for second_level_item in item:
                    yield second_level_item