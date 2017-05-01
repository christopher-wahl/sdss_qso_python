import os
import sys
from multiprocessing import cpu_count, freeze_support

from common.messaging import BETA, GAMMA

""" Easy import of os.path/multi methods """
join = os.path.join
abspath = os.path.abspath
freeze_support = freeze_support  # this just keeps freeze_support import statement from being optimized away

""" Maximum concurrent processes for multiprocessing.  Default value of cpu_count stored in the constant """
MAX_PROC = cpu_count()

""" BASE PATHS """
def get_base_code_path( ) -> str:
    """
    This method finds the path of your code's root folder.  For example, the entirety of this project's code is housed
    in a folder titled "pythonqso".  Regardless of where I start a program, I will be able to locate the code path within
    that program by invoking either this method, or the constant BASE_CODE_PATH this is called by shortly afterwards.
    :return: 
    """
    path = os.getcwd( )
    while (os.path.split( path )[ 1 ] != "pythonqso"):
        path = os.path.split( path )[ 0 ]
    return os.path.abspath( path )


ROOT_DRIVE_PATH = "/media/christopher/Research" if sys.platform == "linux" else "D:/"

BASE_CODE_PATH = get_base_code_path( )
if BASE_CODE_PATH not in sys.path:
    sys.path.insert( 0, BASE_CODE_PATH )

BASE_DATA_PATH = abspath( join( ROOT_DRIVE_PATH, "Data" ) )
BASE_ANALYSIS_PATH = join( BASE_DATA_PATH, "Analysis" )
BASE_SPEC_PATH = join( BASE_DATA_PATH, "Spec" )
SOURCE_SPEC_PATH = join( BASE_SPEC_PATH, "Source" )
BINNED_SPEC_PATH = join( BASE_SPEC_PATH, "BINNED" )
REST_SPEC_PATH = join( BINNED_SPEC_PATH, "REST" )
BASE_PLOT_PATH = join( BASE_DATA_PATH, "Plot" )

""" DEFAULT VALUES """
DEFAULT_SCALE_WL = 4767
DEFAULT_SCALE_RADIUS = 18
STD_MIN_WL = 2850
STD_MAX_WL = 4785
MGII_RANGE = (2680, 2910)
HG_RANGE = (4250, 4400)
HB_RANGE = ( 4750, 4950 )
OIII_RANGE = (4950, 5050)
CONT_RANGE = (MGII_RANGE[ 1 ], HB_RANGE[ 0 ])
CHI_BASE_MAG = 20



RANGE_STRING_DICT = { MGII_RANGE: "MgII", HG_RANGE: f"H{GAMMA}", HB_RANGE: f"H{BETA}", OIII_RANGE: "OIII",
                      CONT_RANGE: "Continuum" }

""" MISC VALUES """
SHEN_FOLDER = join( BASE_DATA_PATH, "Shen" )
SHEN_FIT_FILE = join( SHEN_FOLDER, "dr7_bh_May_2011.fits" )
