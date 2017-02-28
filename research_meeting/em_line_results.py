# TODO: All of this
import logging

from common.constants import BASE_PLOT_PATH, BASE_PROCESSED_PATH, join
from fileio.list_dict_utils import namestring_dict_reader
from fileio.spec_load_write import async_rspec, rspecLoader
from spectrum.utils import scale_enmasse
from tools.list_dict import key_value_dict_to_paired_list, sort_list_by_shen_key
from tools.plot import ab_z_plot, four_by_four_multiplot


def main( n: int, chi: int, min_count: float ):
    # load results
    FOLDER_STR = f"Sigma {n} - Max {chi}"
    BASE_INTEREST = join( BASE_PROCESSED_PATH, "Chi Matching", "EM Lines" )
    PROGRAM_PATH = join( BASE_INTEREST, FOLDER_STR )
    INDI_PATH = join( PROGRAM_PATH, "Individual Matches" )
    PLOT_PATH = join( BASE_PLOT_PATH, "EM Line Matching", FOLDER_STR )

    results_dict = namestring_dict_reader( PROGRAM_PATH, 'results.csv', has_header=False )

    # Restrict to the top Chi = 20
    results_list = list(
        filter( lambda x: x[ 1 ] > min_count, key_value_dict_to_paired_list( results_dict, True, True ) ) )

    # Plot out
    i, n = 1, len( results_list )
    logging.info( "Beginning plot" )
    for result in results_list:
        r_dict = namestring_dict_reader( INDI_PATH, f"{result[ 0 ]}.csv" )
        titlestr = f"{result[ 0 ]} - EM Line - Chi={chi} Sigma={n} Count={result[1]}"
        ab_z_plot( PLOT_PATH, f"{result[ 0 ]} - {result[ 1 ]}.pdf", result[ 0 ], r_dict, titlestr, n_sigma=n )
        primary = rspecLoader( result[ 0 ] )
        speclist = scale_enmasse( primary, *async_rspec( r_dict.keys( ) ) )
        sort_list_by_shen_key( speclist )
        four_by_four_multiplot( rspecLoader( result[ 0 ] ), *speclist, path=PLOT_PATH,
                                filename=f"{result[ 0 ]} - {result[ 1 ]} MULTI.pdf", plotTitle=titlestr )
        print( f"{i}/{n}" )
        i += 1

    logging.info( "Complete" )


if __debug__:
    logging.basicConfig( level=logging.INFO )

if __name__ == '__main__':
    from common import freeze_support

    freeze_support( )
    main( 3, 20, 20 )
