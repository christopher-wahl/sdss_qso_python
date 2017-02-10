import os
import sys
from multiprocessing import cpu_count

join = os.path.join
abspath = os.path.abspath

MAX_PROC = cpu_count()

""" BASE PATHS """
BASE_CODE_PATH = abspath( os.getcwd() )
BASE_PROCESSED_PATH = abspath( "../../Processed" )
BASE_SPEC_PATH = join( BASE_PROCESSED_PATH, "Spec" )
SOURCE_SPEC_PATH = join( BASE_SPEC_PATH, "PSource" )
REST_SPEC_PATH = join( SOURCE_SPEC_PATH, "Rest" )
BINNED_SPEC_PATH = join( REST_SPEC_PATH, "Binned" )

BASE_PLOT_PATH = join( BASE_PROCESSED_PATH, "Plot" )

""" DEFAULT VALUES """
DEFAULT_SCALE_WL = 4767
DEFUALT_SCALE_RADIUS = 18
STD_MIN_WL = 2850
STD_MAX_WL = 4785
MGII_RANGE = ( 2750, 2850 )
HB_RANGE = ( 4785, 4930 )

""" CHARACTERS """
ANGSTROM = r"‎Å"
FLUX_UNITS = r"10^{-17} egs s^{-1} cm^{-2} %s^{-1}" % ANGSTROM
SQUARE = "²"

if sys.platform == "win32":
    ANGSTROM = ANGSTROM.encode('cp1252', errors='replace').decode('cp1252')
    FLUX_UNITS = FLUX_UNITS.encode( 'cp1252', errors='replace' ).decode( 'cp1252' )