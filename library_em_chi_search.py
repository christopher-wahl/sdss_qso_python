from typing import Iterable, List, Tuple, Union

from analysis.chi import pipeline_chi_wrapper
from analysis.pipeline import redshift_ab_pipeline, speclist_analysis_pipeline
from catalog import get_shen_header, get_shen_string, shenCat
from common.constants import BASE_PROCESSED_PATH, HB_RANGE, HG_RANGE, MGII_RANGE, OIII_RANGE, join
from fileio.spec_load_write import async_bspec, bspecLoader
from fileio.utils import dirCheck
from spectrum import Spectrum
from spectrum.tools import scale_enmasse

EM_MAX = 20


def __tabprint( s: str ) -> None:
    print( f"       {s}" )


def loader( nameslist: Union[ List[ str ], Iterable ] ) -> List[ Spectrum ]:
    __tabprint( f"Loading { len( nameslist ) } spectra..." )
    speclist = async_bspec( nameslist )
    __tabprint( "Complete" )
    return speclist


def range_pass( primary: Spectrum, speclist, wl_range: Tuple[ float, float ] ):
    primary.trim( wl_range=wl_range )
    em_pipe = speclist_analysis_pipeline( primary, speclist, pipeline_chi_wrapper, (0, EM_MAX) )
    em_pipe.do_analysis( )
    return em_pipe.reduce_results( ).keys( )


def analyze( primary: str, nameslist: List[ str ], n_sigma: int, OUT_PATH: str ):
    # Run Each EM line & reduce
    __tabprint( f"{primary }" )
    speclist = loader( nameslist )
    speclist = scale_enmasse( bspecLoader( primary ), *speclist )

    __tabprint( "MGII Analysis..." )
    results = range_pass( bspecLoader( primary ), speclist, MGII_RANGE )
    if len( results ) == 0:
        return 0
    for i in range( len( speclist ) - 1, -1, -1 ):
        if speclist[ i ].getNS() not in results:
            del speclist[ i ]

    __tabprint( "HB Analysis..." )
    results = range_pass( bspecLoader( primary ), speclist, HB_RANGE )
    if len( results ) == 0:
        return 0
    for i in range( len( speclist ) - 1, -1, -1 ):
        if speclist[ i ].getNS() not in results:
            del speclist[ i ]

    __tabprint( "OIII Analysis..." )
    results = range_pass( bspecLoader( primary ), speclist, OIII_RANGE )
    if len( results ) == 0:
        return 0
    for i in range( len( speclist ) - 1, -1, -1 ):
        if speclist[ i ].getNS() not in results:
            del speclist[ i ]

    __tabprint( "HG Analysis..." )
    results = range_pass( bspecLoader( primary ), speclist, HG_RANGE )
    if len( results ) == 0:
        return 0
    for i in range( len( speclist ) - 1, -1, -1 ):
        if speclist[ i ].getNS() not in results:
            del speclist[ i ]

    # Redshift reduction
    __tabprint( "Redshift Reduction..." )
    z_pipe = redshift_ab_pipeline( primary_ns=primary, ns_of_interest=list( results ) )
    results = z_pipe.reduce_results( n_sigma )

    # Write results
    with open( join( OUT_PATH, f"{primary}.csv" ), 'w' ) as outfile:
        outfile.write( get_shen_header( CR=True ) )
        outfile.writelines( [ get_shen_string( k, CR=True ) for k in results ] )
    # Return count
    return len( results )


def main( n_sigma: int ):
    BASE_OUTPATH = join( BASE_PROCESSED_PATH, "Chi Matching", "EM Lines", f"Sigma {n_sigma} - Max {EM_MAX}" )
    CAT_WRITE_PATH = join( BASE_OUTPATH, "Individual Matches" )

    shenCat.load( )
    names = shenCat.keys( )
    dirCheck( CAT_WRITE_PATH )
    count_dict = { }
    n = len( names )
    for i in range( n ):
        primary = names.pop( i )
        count_dict[ primary ] = count = analyze( primary, names, n_sigma, CAT_WRITE_PATH )

        with open( join( BASE_OUTPATH, 'running_count.csv' ), 'a' ) as outfile:
            outfile.write( f"{primary},{count}\n" )

        names.insert( i, primary )

        print( f"{ primary } : { count_dict[ primary ] } -> { i + 1 } / { n }" )
    print( "Writing final counts..." )

    from tools.list_dict import key_value_dict_to_paired_list
    nl = key_value_dict_to_paired_list( count_dict, True )

    with open( join( BASE_OUTPATH, "results.csv" ), "w" ) as outfile:
        for k, v in count_dict.items( ):
            outfile.write( f"{k},{v}\n" )

    print( "Done." )


if __name__ == '__main__':
    from common import freeze_support

    freeze_support( )
    main( 3 )
