from typing import List

from common.constants import SHEN_FIT_FILE
from common.messaging import linesep
from .catalog import catalog

shenCat = catalog( catalog.SHEN_CATALOG )
shenCat.load( )

def get_shen_string( namestring: str, *append_values, CR: bool = False ) -> str:
    """
    Any values which are passed after namestring will be appended to the out_str in the
    order in which they are passed.  Appending method adds each value as f",{value}"

    If CR = True is passed, a carraige return will be appended at the end of the string.
    :param namestring:
    :param append_values:
    :return:
    """
    out_str = namestring
    for k in get_shen_key_list():
        if k == "namestring":
            continue
        out_str += f",{shenCat.subkey( namestring, k )}"
    for v in append_values:
        out_str += f",{append_values}"
    if CR:
        out_str += linesep
    return out_str


def get_shen_key_list() -> List[ str ]:
    """
    Returns an alphabetic list of of the subkeys in the shenCat.  Also inserts the value "namestring" into the first
    position of the list.  This is intended to feed the namestring dict writing processes 
    get_shen_string and get_shen_header
    
    :return: A list of [ "namestring", ... shenCat subkeys ]
    :rtype: str
    """
    first = next( iter( shenCat.values() ) )
    subkeys = sorted( first.keys() )
    subkeys.insert( 0, "namestring" )
    return subkeys


def get_shen_header( CR: bool = False ) -> str:
    """
    Returns a CSV formatted header string of namestring,...shenCat subkeys,...
    
    :param CR: Defaults to False.  If True, appends a line return to the returned string 
    :return: Formatted header string
    :rtype: str
    """
    out_str = ''.join( f"{key}," for key in get_shen_key_list() )[ :-1 ]
    if CR:
        out_str += linesep
    return out_str


def load_shen_source( path: str = SHEN_FIT_FILE ) -> tuple:
    """
    Returns ( header, data ) where header is the 2nd layer:  getheader( FIT_FILE, 1 )

    Print header[ key ] for key in header to access field names, noting that the
    numbering given beings at 1.  Thus, to access that field, subtract 1 from it (Python
    starts counting at 0).

    data[ 6 ] = MJD
    data[ 4 ] = PLATE
    data[ 5 ] = FIBER

    data[ 142 ] = Z_HW
    data[ 143 ] = Z_HW_ERR

    :param path:
    :return: tuple
    """
    from astropy.io.fits import getdata, getheader
    header = getheader( SHEN_FIT_FILE, 1 )
    data = getdata( SHEN_FIT_FILE )

    return header, data


def get_source_ns( fits_record ) -> str:
    return "%05i-%04i-%03i" % (fits_record[ 6 ], fits_record[ 4 ], fits_record[ 5 ])
