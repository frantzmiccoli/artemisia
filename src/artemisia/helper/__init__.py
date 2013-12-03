import re


class Helper:
    """
    This class provides a helper well suited for the rest of the manipulation
    It's handling column name manipulation
    """

    def __init__(self):
        self._sql_function_re = re.compile('^\s*\w*\s*\((.*)\)\s*$')

    def clean_columns(self, columns):
        """
        Clean column names by removing duplicates. this function takes a list
        and return a list
        """
        columns = list(set(columns))

        if None in columns:
            columns.remove(None)

        return columns

    def is_sql_function(self, column):
        """
        Tell whether or not the given column may be corresponding to an SQL
        function (SQL function must be set as target column within the
        aggregator)
        """
        match = self._sql_function_re.match(column)
        return match is not None