"""init function"""
from os.path import dirname, basename, isfile
import glob

"""get dirname"""
modules = glob.glob(dirname(__file__)+"/*.py")
__all__ = [ basename(f)[:-3] for f in modules if isfile(f)]
