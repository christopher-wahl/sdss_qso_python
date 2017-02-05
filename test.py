from multiprocessing import Pool, freeze_support

from analysis.chi import chi
from catalog import shenCat
from common.constants import BASE_PROCESSED_PATH, BINNED_SPEC_PATH
from fileio.spec_load_write import async_load
from fileio.utils import join, object_writer


def __multi_wrapper( inputV ):
    pSpec, oSpec = inputV
    c = chi( pSpec, oSpec, True )
    return { oSpec.getNS( ): c }


def multichi( primespec, speclist ):
    pool = Pool()
    inputlist = [ ( primespec, ospec ) for ospec in speclist ]
    results = pool.imap_unordered( __multi_wrapper, inputlist )
    pool.close()
    pool.join()

    outdict = {}
    for r in results:
        outdict.update( r )

    return outdict

if __name__ == "__main__":
    freeze_support()

    shenCat.load()
    nslist = shenCat.keys()

    speclist = async_load( BINNED_SPEC_PATH, nslist, ".bspec" )
    outpath = join( BASE_PROCESSED_PATH, "chi" )

    for spec in speclist:
        from common.constants import STD_MIN_WL, STD_MAX_WL
        spec.trim( STD_MIN_WL, STD_MAX_WL )
    print( "Spectra timmed" )
    bigD = {}
    for i in range( len( nslist ) ):
        spec = speclist.pop( i )
        print( f"{i} : { spec.getNS() }" )
        chiD = multichi( spec, speclist ) # async_chi_analysis( spec, speclist )
        print( " -- Done" )
        object_writer( chiD, outpath, f"{ spec.getNS() }-chi.bin")
        bigD[ spec.getNS() ] = chiD.copy()

        speclist.insert( i, spec )


    print( "Writing big file")
    object_writer( bigD, BASE_PROCESSED_PATH, "chiCatalog.bin" )