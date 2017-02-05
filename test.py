from analysis.chi import async_chi_analysis
from catalog import shenCat
from common.constants import BINNED_SPEC_PATH
from fileio.spec_load_write import async_load

shenCat.load()

speclist = async_load( BINNED_SPEC_PATH, shenCat.keys(), ".bspec" )
spec = speclist.pop( 0 )

chiD = async_chi_analysis( spec, speclist )