from itertools import cycle
import types
import numpy

from matplotlib_wrapper import MatplotlibWrapper
import artemisia.aggregator as gaggregator
import artemisia.helper as ghelper


class Viewer:
    """
    This class is wrapping matplotlib and is meant to provide an easy access
    by letting the end user plotting data, by just providing a data generator
    and the relevant element for plotting
    """

    def __init__(self):
        self._helper = ghelper.Helper()
        self._matplotlib_wrapper = None
        self._init_attributes()

    def plot(self, *args, **kwargs):
        args = list(args)
        data_generator = args.pop(0)
        self._axis_columns = args
        self._color_column = kwargs.get('color_column', None)
        if (self._color_column is not None) \
                & (self._color_column not in self._axis_columns):
            self._axis_columns.append(self._color_column)
        self._output_file_name = kwargs.get('output_file_name', 'out.png')
        self._y_label = kwargs.get('y_label', None)
        self._scatter = kwargs.get('scatter', False)
        if ((self._color_column is not None) & (len(self._axis_columns) > 3))\
                | ((self._color_column is None)
                    & (len(self._axis_columns) > 2)):
            raise Exception("Unexpected axis count")

        self._xy_axis_columns = list(self._axis_columns[:])
        if (not self._scatter) & (self._color_column is not None):
            self._xy_axis_columns.remove(self._color_column)
        if len(self._xy_axis_columns) < 2:
            self._xy_axis_columns.append('aggregate')

        aggregate = self._get_aggregate(data_generator, self._axis_columns)
        plot_ready_values = self._get_plot_ready_values(aggregate,
                                                        self._xy_axis_columns)

        self._plot(plot_ready_values)

    def _init_attributes(self):
        self._color_column = None
        self._output_file_name = None
        self._y_label = None
        self._scatter = None
        self._axis_columns = None
        self._xy_axis_columns = None
        self._aggregate = None
        self._plot_ready_values = None


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

    def _plot(self, plot_ready_values):
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
                    self._x_values_set += list(set(x)
                                               - set(self._x_values_set))
                    indexes = map(lambda x_value:
                                  self._x_values_set.index(x_value), x)
                    marker = color + "."
                    self._get_matplotlib_wrapper()\
                        .plot(indexes, y, marker,label=color_column_value)
                else:
                    color_pushed = False
                    for x_value in x:
                        index = x.index(x_value)
                        if not color_pushed:
                            label = color_column_value
                            color_pushed = True
                        else:
                            label = None
                        self._get_matplotlib_wrapper()\
                            .bar(index, y[index], bar_width, color=color,
                                 label=label)
                        self._get_matplotlib_wrapper()\
                            .xticks(numpy.arange(len(x)) + (bar_width / 2), x)
            else:
                marker = color + "."
                self._get_matplotlib_wrapper()\
                    .plot(x, y, marker, label=color_column_value)

        legend = None
        if x_axis_is_string:
            self._get_matplotlib_wrapper().xlabel(self._xy_axis_columns[0])
            self._get_matplotlib_wrapper().ylabel(self._xy_axis_columns[1])
            if self._scatter:
                self._get_matplotlib_wrapper()\
                    .xlim([-0.1, len(self._x_values_set) - 0.9])
        else:
            self._get_matplotlib_wrapper().xlabel(self._xy_axis_columns[0])
            if self._y_label is None:
                self._y_label = self._xy_axis_columns[1]
            self._get_matplotlib_wrapper().ylabel(self._y_label)

        if self._color_column is not None:
            legend = self._get_matplotlib_wrapper() \
                .legend(loc='lower right', numpoints=1)

        if legend is not None:
            legend.get_frame().set_alpha(0.7)

        self._get_matplotlib_wrapper().subplots_adjust(left=0.15)

        #avoid big margins (should be sent as an argument
        self._get_matplotlib_wrapper().tight_layout()
        self._get_matplotlib_wrapper().savefig(self._output_file_name)

    def _get_matplotlib_wrapper(self):
        if self._matplotlib_wrapper is None:
            self._matplotlib_wrapper = MatplotlibWrapper()
        return self._matplotlib_wrapper
