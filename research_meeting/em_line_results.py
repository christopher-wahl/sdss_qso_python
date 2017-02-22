# TODO: All of this

from common.constants import BASE_PROCESSED_PATH, join
from fileio.list_dict_utils import namestring_dict_reader
from fileio.utils import fns, getFiles


def main( ):
    primary_ns = "53770-2376-290"
    BASE_IN_PATH = join( BASE_PROCESSED_PATH, "Chi Matching/EM Lines/Sigma 3 - Max 20/" )
    I_PATH = join( BASE_IN_PATH, "Individual Matches" )
    results_list = namestring_dict_reader( BASE_IN_PATH, getFiles( BASE_IN_PATH, '.csv' )[ 0 ], has_header=False )
    filelist = getFiles( I_PATH, '.csv' )

    indi_dict = { }
    for f in filelist:
        indi_dict[ fns( f ) ] = namestring_dict_reader( I_PATH, f )

    print( results_list[ primary_ns ] )


if __name__ == '__main__':
    from common import freeze_support

    freeze_support( )
    main( )
