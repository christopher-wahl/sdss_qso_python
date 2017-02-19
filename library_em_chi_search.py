from typing import Iterable, List, Tuple, Union

from analysis.chi import pipeline_chi_wrapper
from analysis.pipeline import redshift_ab_pipeline, speclist_analysis_pipeline
from catalog import get_shen_header, get_shen_string, shenCat
from common.constants import BASE_PROCESSED_PATH, HB_RANGE, HG_RANGE, MGII_RANGE, OIII_RANGE, join
from fileio.spec_load_write import async_bspec, bspecLoader
from fileio.utils import dirCheck
from spectrum import Spectrum

EM_MAX = 300


def __tabprint( s: str ) -> None:
    print( f"       {s}" )


def loader( nameslist: Union[ List[ str ], Iterable ] ) -> List[ Spectrum ]:
    __tabprint( f"Loading { len( nameslist ) } spectra..." )
    speclist = async_bspec( nameslist )
    __tabprint( "Complete" )
    return speclist


def range_pass( primary: Spectrum, nameslist: Union[ List[ str ], Iterable ], wl_range: Tuple[ float, float ] ):
    speclist = loader( nameslist )
    primary.trim( wl_range=wl_range )
    em_pipe = speclist_analysis_pipeline( primary, speclist, pipeline_chi_wrapper, (0, EM_MAX) )
    em_pipe.do_analysis( )
    return em_pipe.reduce_results( ).keys( )


def analyze( primary: str, nameslist: List[ str ], n_sigma: int, OUT_PATH: str ):
    # Run Each EM line & reduce
    print( f"{primary } - MGII Analysis..." )
    nameslist = range_pass( bspecLoader( primary ), nameslist, MGII_RANGE )
    __tabprint( "HB Analysis..." )
    nameslist = range_pass( bspecLoader( primary ), nameslist, HB_RANGE )
    __tabprint( "OIII Analysis..." )
    nameslist = range_pass( bspecLoader( primary ), nameslist, OIII_RANGE )
    __tabprint( "HG Analysis..." )
    nameslist = range_pass( bspecLoader( primary ), nameslist, HG_RANGE )

    # Redshift reduction
    __tabprint( "Redshift Reduction..." )
    z_pipe = redshift_ab_pipeline( primary_ns=primary, ns_of_interest=list( nameslist ) )
    results = z_pipe.reduce_results( n_sigma )

    # Write results
    with open( join( OUT_PATH, f"{primary}.csv" ), 'w' ) as outfile:
        outfile.write( get_shen_header( CR=True ) )
        outfile.writelines( [ get_shen_string( k, CR=True ) for k in results ] )
    # Return count
    return len( results )


def main( n_sigma: int ):
    BASE_OUTPATH = join( BASE_PROCESSED_PATH, "Chi Matching", "EM Lines", f"Sigma {n_sigma}" )
    CAT_WRITE_PATH = join( BASE_OUTPATH, "Individual Matches" )

    shenCat.load( )
    names = shenCat.keys( )
    dirCheck( CAT_WRITE_PATH )
    count_dict = { }
    n = len( names )
    for i in range( n ):
        primary = names.pop( i )
        count_dict[ primary ] = analyze( primary, names, n_sigma, CAT_WRITE_PATH )

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
