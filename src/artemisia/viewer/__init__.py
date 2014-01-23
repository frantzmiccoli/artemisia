import matplotlib
import artemisia.aggregator as gaggregator
import artemisia.helper as ghelper

matplotlib.use('Agg') # works better in Vagrant
import pylab
try:
    import seaborn
except ImportError:
    print 'seaborn is not available, the final result could be more pretty'

from itertools import cycle
import types
import numpy


class Viewer:
    """
    This class is wrapping matplotlib and is meant to provide an easy access
    by letting the end user plotting data, by just providing a data generator
    and the relevant element for plotting
    """

    def __init__(self):
        self._helper = ghelper.Helper()

    def plot(self, *args, **kwargs):
        args = list(args)
        data_generator = args.pop(0)
        axis_columns = args
        self._color_column = kwargs.get('color_column', None)
        if (self._color_column is not None) & (self._color_column not in axis_columns):
            axis_columns.append(self._color_column)
        self._output_file_name = kwargs.get('output_file_name', 'out.png')
        self._y_label = kwargs.get('y_label', None)
        self._scatter = kwargs.get('scatter', False)
        if ((self._color_column is not None) & (len(axis_columns) > 3))\
            | ((self._color_column is None) & (len(axis_columns) > 2)):
            raise Exception("Unexpected axis count")

        xy_axis_columns = list(axis_columns[:])
        if (not self._scatter) & (self._color_column is not None):
            xy_axis_columns.remove(self._color_column)
        if len(xy_axis_columns) < 2:
            xy_axis_columns.append('aggregate')

        aggregate = self._get_aggregate(data_generator, axis_columns)
        plot_ready_values = self._get_plot_ready_values(aggregate, xy_axis_columns)

        self._plot(plot_ready_values, xy_axis_columns)

        #avoid big margins (should be sent as an argument
        pylab.tight_layout()

        pylab.savefig(self._output_file_name)

    def _get_aggregate(self, data_generator, axis_columns):
        aggregator = gaggregator.Aggregator()
        for axis_column in axis_columns:
            if not self._helper.is_sql_function(axis_column):
                aggregator.add_aggregate_column(axis_column)
            else:
                aggregator.set_target_value(axis_column)

        aggregate = aggregator.aggregate(data_generator)
        return aggregate

    def _get_plot_ready_values(self, aggregate, xy_axis_columns):
        prepared_data = {}
        for value_point in aggregate:
            if self._color_column is not None:
                color_column_value = value_point[self._color_column]
            else:
                color_column_value = None

            if color_column_value not in prepared_data.keys():
                prepared_data[color_column_value] = ([], [])

            x_values, y_values = prepared_data[color_column_value]
            x_values.append(value_point[xy_axis_columns[0]])
            y_values.append(value_point[xy_axis_columns[1]])
        return prepared_data

    def _plot(self, plot_ready_values, xy_axis_columns):
        self._x_values_set = []
        colors = cycle("rgcmykb")
        x_axis_is_string = False

        for color_column_value in plot_ready_values.keys():
            color = colors.next()
            x, y = plot_ready_values[color_column_value]
            if (isinstance(y[0], types.StringType)) | \
                    (isinstance(y[0], types.UnicodeType)):
                tmp = x
                x = y
                y = tmp

            if (isinstance(x[0], types.StringType)) | \
                    (isinstance(x[0], types.UnicodeType)):
                x_axis_is_string = True
                bar_width = 0.5
                if self._scatter:
                    self._x_values_set += list(set(x) - set(self._x_values_set))
                    indexes = map(lambda x_value: self._x_values_set.index(x_value), x)
                    marker = color + "."
                    pylab.plot(indexes, y, marker, label=color_column_value)
                else:
                    for x_value in x:
                        index = x.index(x_value)
                        pylab.bar(index, y[index], bar_width, color=color,
                          label=x_value)
                        pylab.xticks(numpy.arange(len(x)) + (bar_width / 2), x)
            else:
                marker = color + "."
                pylab.plot(x, y, marker, label=color_column_value)

        legend = None
        if x_axis_is_string:
            pylab.xlabel(xy_axis_columns[0])
            pylab.ylabel(xy_axis_columns[1])
            if self._scatter:
                pylab.xlim([-0.1, len(self._x_values_set) - 0.9])
                legend = pylab.legend(loc='lower right', numpoints=1)
        else:
            pylab.xlabel(xy_axis_columns[0])
            if self._y_label is None:
                self._y_label = xy_axis_columns[1]
            pylab.ylabel(self._y_label)
            legend = pylab.legend(loc='lower right', numpoints=1)

        if legend is not None:
            legend.get_frame().set_alpha(0.7)

        pylab.subplots_adjust(left=0.15)

