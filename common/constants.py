import os
from sys import path
if os.path.abspath( "../" ) not in path:
    path.insert( 0, os.path.abspath( "../" ) )
join = os.path.join
abspath = os.path.abspath

from multiprocessing import cpu_count
MAX_PROC = cpu_count()

""" BASE PATHS """
BASE_CODE_PATH = abspath( os.getcwd() )
BASE_PROCESSED_PATH = abspath( "../../Processed" )
BASE_SPEC_PATH = join( BASE_PROCESSED_PATH, "Spec" )
SOURCE_SPEC_PATH = join( BASE_SPEC_PATH, "PSource" )
REST_SPEC_PATH = join( SOURCE_SPEC_PATH, "Rest" )
BINNED_SPEC_PATH = join( REST_SPEC_PATH, "Binned" )

""" DEFAULT VALUES """
DEFAULT_SCALE_WL = 4767
DEFUALT_SCALE_RADIUS = 18
STD_MIN_WL = 2750
STD_MAX_WL = 4785


