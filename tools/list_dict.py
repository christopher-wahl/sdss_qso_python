from typing import Dict, List, Tuple, Union

from spectrum import Spectrum


def paired_list_to_dict( paired_list: List[ Tuple ] ) -> Dict:
    """
    Converts a list of [ ( a, b ), ( c, d ) ... ] or [ { a : b }, { c : d } ... ]
    to a dictionary: {  a : b, c : d ... }

    If the entires of paired_list are not either a dictionary or a tuple/list of length 2, raises Attribute Error

    :param paired_list:
    :return:
    """

    def __err( ):
        raise TypeError(
                "paired_list_to_dict: paired_list entries must be either dict or have a length of 2\nFirst entry: %s" %
                paired_list[ 0 ] )

    out_dict = { }
    for point in paired_list:
        if type( point ) == dict:
            out_dict.update( point )
        elif len( paired_list[ 0 ] ) == 2:
            out_dict.update( { point[ 0 ]: point[ 1 ] } )
        else:
            __err( )

    return out_dict


def paired_tuple_list_to_two_lists( inlist ) -> Tuple[ List, List ]:
    xlist, ylist, zlist = zip( *inlist )
    return list( xlist ), list( ylist )


def sort_list_by_shen_key( in_list: Union[ List[ Spectrum ], List[ str ] ], sort_key='z' ) -> List:
    """
    Takes in a list of either Spectrum or namestrings and sorts them by a key used in shenCat, ascending values.
    If sort_key is not specified, defaults to redshift key 'z'

    :param in_list:
    :param sort_key:
    :type in_list: list
    :type sort_key: str
    :return:
    :rtype: list
    """
    from catalog import shenCat
    def _sort_key( x: Union[ Spectrum, str ] ) -> float:
        return shenCat.subkey( x.getNS( ) if isinstance( x, Spectrum ) else x, sort_key )

    shenCat.load( )
    if not isinstance( in_list, list ):
        in_list = list( in_list )
    in_list.sort( key=_sort_key )
    return in_list


def key_value_dict_to_paired_list( in_dict: dict, sort: bool = False, reverse: bool = False ) -> List[ Tuple ]:
    """

    :param in_dict:
    :param sort: If True, will sort by the value of the dictionary
    :param reverse: Used in conjunction with sort, if True, sorts the value in descending order.
    :type in_dict: dict
    :type sort: bool
    :type reverse: bool
    :return: List of ( key, value ) tuple pairs
    :rtype: list
    """
    klist = list( in_dict.keys( ) )
    vlist = [ in_dict[ k ] for k in klist ]

    outlist = list( zip( klist, vlist ) )

    if sort:
        outlist.sort( key=lambda x: x[ 1 ], reverse=reverse )

    return outlist
    pass
