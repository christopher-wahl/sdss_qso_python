from analysis.chi import multi_chi_analysis
from catalog import shenCat
from common.constants import BINNED_SPEC_PATH, freeze_support
from fileio.spec_load_write import async_load

if __name__ == "__main__":
    freeze_support()
    shenCat.load()
    fns = [ f"{ns}.bspec" for ns in shenCat.keys() ]
    speclist = async_load( BINNED_SPEC_PATH, fns[ : 11 ] )

    oD = multi_chi_analysis( speclist.pop( 0 ), speclist )

    for k, v in oD.items():
        print( k, v )
