import matplotlib
matplotlib.use('Agg')  # works better in Vagrant
import pylab
try:
    import seaborn
except ImportError:
    print 'seaborn is not available, the final result could be more pretty'


class MatplotlibWrapper:

