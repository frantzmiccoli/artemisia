import matplotlib
matplotlib.use('Agg')  # works better in Vagrant
import pylab
try:
    import seaborn
except ImportError:
    print 'seaborn is not available, the final result could be more pretty'
import types


class MatplotlibWrapper:

    def __getattr__(self, name, *args, **kwargs):
        attr = getattr(pylab, name)
        if isinstance(attr, types.FunctionType):
            def wrapped_function(*args, **kwargs):
                return attr(*args, **kwargs)
            return wrapped_function
        return attr

