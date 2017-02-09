from typing import List, Union

from spectrum import Spectrum


def paired_list_to_dict( paired_list ):
    """
    Converts a list of [ ( a, b ), ( c, d ) ... ] or [ { a : b }, { c : d } ... ]
    to a dictionary: {  a : b, c : d ... }

    If the entires of paired_list are not either a dictionary or a tuple/list of length 2, raises Attribute Error

    :param paired_list:
    :return:
    """
    def __err():
        raise TypeError(
                "paired_list_to_dict: paired_list entries must be either dict or have a length of 2\nFirst entry: %s" %
                paired_list[ 0 ] )

    out_dict = {}
    for point in paired_list:
        if type( point ) == dict:
            out_dict.update( point )
        elif len( paired_list[ 0 ] ) == 2:
            out_dict.update( { point[ 0 ] : point[ 1 ] } )
        else: __err()

    return out_dict

def paired_tuple_list_to_two_lists( inlist ):
    xlist, ylist, zlist = zip( * inlist )
    return list( xlist ), list( ylist )


def sort_list_by_shen_key( in_list: Union[ List[ Spectrum ], List[ str ] ], sort_key='z' ):
    from catalog import shenCat
    def _sort_key( x: Union[ Spectrum, str ] ) -> float:
        return shenCat.subkey( x.getNS( ) if isinstance( x, Spectrum ) else x, sort_key )

    shenCat.load( )
    in_list.sort( key=_sort_key )
    return in_list
