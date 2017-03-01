from typing import List

from analysis.chi import pipeline_chi_wrapper
from analysis.pipeline import redshift_ab_pipeline, speclist_analysis_pipeline
from catalog import shenCat
from common.constants import BASE_PLOT_PATH, BINNED_SPEC_PATH, freeze_support, join
from fileio.spec_load_write import async_load, bspecLoader
from spectrum import Spectrum, drop_to_em_lines, scale_enmasse
from tools.plot import four_by_four_multiplot


def do_Chi( primary : Spectrum, speclist : List[ Spectrum ], chi_limit : float ) -> dict:
    chi_a = speclist_analysis_pipeline( primary, speclist, pipeline_chi_wrapper, ( 0, chi_limit ) )
    chi_a.do_analysis()
    return chi_a.reduce_results()

def main():
    shenCat.load()

    ns = "53521-1714-011"
    outpath = join( BASE_PLOT_PATH, f"{ns} EM Line" )
    z, ab, aberr = shenCat.subkey( ns, 'z', 'ab', 'ab_err' )

    namelist = shenCat.keys()
    del namelist[ namelist.index( ns ) ]
    init_results_dict = {}
    for name in namelist:
        init_results_dict[ name ] = 0
    primary = bspecLoader( ns )
    dupe_primary = primary.cpy()

    rmp = redshift_ab_pipeline( ns, z, ab, aberr, init_results_dict )
    r = rmp.reduce_results( 3 )
    rmp.plot_results( outpath, f"{ns} AB v Z.pdf" )

    print( "Loading speclist" )
    speclist = async_load( BINNED_SPEC_PATH, r.keys(), 'bspec' )
    dupelist = async_load( BINNED_SPEC_PATH, r.keys(), "bspec" )

    speclist.sort( key = lambda x: shenCat.subkey( x.getNS(), 'z' ) )
    dupelist.sort( key = lambda x: shenCat.subkey( x.getNS(), 'z' ) )
    for d in dupelist:
        d.setNS( f"{d.getNS()}: z={shenCat.subkey( d.getNS(), 'z')}" )

    scale_enmasse( primary, *speclist )
    scale_enmasse( primary, *dupelist )
    speclist = drop_to_em_lines( primary, *speclist )
    primary = speclist.pop( 0 )

    n = 500
    print( "Doing chi analysis at n = %i" % n )
    r = do_Chi( primary, speclist, n )
    for i in range( len( speclist ) - 1, -1, -1 ):
        if speclist[ i ].getNS() not in r:
            del speclist[ i ]
            del dupelist[ i ]
        else:
            dupelist[ i ].setNS( f"{dupelist[ i ].getNS()} : {r[ speclist[ i ].getNS() ]}")
    four_by_four_multiplot( dupe_primary, dupelist, path=outpath,
                            filename=f"{ns} EM Line Matches - Upper Limit {n}.pdf",
                            plotTitle=f"{ns} EM Line Matches - Upper Limit {n}" )
    rmp.set_results( r )
    rmp.plot_results( outpath, f"{ns} AB v Z EM Line Chi Matching - Upper Limit {n}.pdf")

    n = 100
    print( "Doing chi analysis at n = %i" % n )
    r = do_Chi( primary, speclist, n )
    for i in range( len( speclist ) - 1, -1, -1 ):
        if speclist[ i ].getNS( ) not in r:
            del speclist[ i ]
            del dupelist[ i ]
    four_by_four_multiplot( dupe_primary, dupelist, path=outpath,
                            filename=f"{ns} EM Line Matches - Upper Limit {n}.pdf",
                            plotTitle=f"{ns} EM Line Matches - Upper Limit {n}" )
    rmp.set_results( r )

    rmp.plot_results( outpath, f"{ns} AB v Z EM Line Chi Matching - Upper Limit {n}.pdf" )

if __name__ == "__main__":
    freeze_support()
    main()