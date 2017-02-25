import os
import sys
from multiprocessing import cpu_count

join = os.path.join
abspath = os.path.abspath
linesep = os.linesep

MAX_PROC = cpu_count()

""" BASE PATHS """


def get_base_code_path( ) -> str:
    path = os.getcwd( )
    while (os.path.split( path )[ 1 ] != "pythonqso"):
        path = os.path.split( path )[ 0 ]
    return os.path.abspath( path )


BASE_CODE_PATH = get_base_code_path( )
BASE_PROCESSED_PATH = abspath( "../../Processed" )
BASE_SPEC_PATH = join( BASE_PROCESSED_PATH, "Spec" )
BINNED_SPEC_PATH = join( BASE_SPEC_PATH, "BIN SOURCE" )
REST_SPEC_PATH = join( BINNED_SPEC_PATH, "REST" )
SOURCE_SPEC_PATH = join( BASE_SPEC_PATH, "PSource" )
OLD_REST_PATH = join( SOURCE_SPEC_PATH, "Rest" )
OLD_BINNED_PATH = join( OLD_REST_PATH, "Binned" )

BASE_PLOT_PATH = join( BASE_PROCESSED_PATH, "Plot" )

""" DEFAULT VALUES """
DEFAULT_SCALE_WL = 4767
DEFAULT_SCALE_RADIUS = 18
STD_MIN_WL = 2850
STD_MAX_WL = 4785
MGII_RANGE = ( 2680, 2910 )#( 2750, 2850 )
HG_RANGE = (4250, 4400)
HB_RANGE = ( 4750, 4950 )
OIII_RANGE = (4950, 5050)
CONT_RANGE = (STD_MIN_WL, STD_MAX_WL)

""" CHARACTERS """
ANGSTROM = r"‎Å"
FLUX_UNITS = r"10^{-17} egs s^{-1} cm^{-2} %s^{-1}" % ANGSTROM
SQUARE = "²"

if sys.platform == "win32":
    ANGSTROM = ANGSTROM.encode('cp1252', errors='replace').decode('cp1252')
    FLUX_UNITS = FLUX_UNITS.encode( 'cp1252', errors='replace' ).decode( 'cp1252' )