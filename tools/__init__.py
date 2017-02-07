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

def compound_dict_writer( inDict : dict, path : str, filename : str, top_key : str = "namestring", sub_keys : list = None ) -> None:
    from fileio.utils import dirCheck, join
    from common.constants import os

    dirCheck( path )
    namekeys = list( inDict.keys() )
    if type( inDict[ namekeys[ 0 ] ] ) == dict:
        sub_keys = sorted( [ f"{sub_key}" for sub_key in inDict[ namekeys[ 0 ] ].keys() ] )
        sub_string = lambda x: ''.join( [ f"{x[ k ]}," for k in sub_keys ] )[:-1] + os.linesep
    elif type( inDict[ namekeys[ 0 ] ] ) == list:
        sub_string = lambda x: ''.join( f'{item},' for item in x )[:-1] + os.linesep
    else:
        sub_string = lambda x: f"{x}{os.linesep}"

    with open( join( path, filename ), 'w' ) as outfile:
        if sub_keys is not None:
            outfile.write( f'{top_key},' + ''.join( [ f"{sk}," for sk in sub_keys ] )[:-1] + os.linesep )
        outfile.writelines( f"{key},{sub_string( inDict[ key ] )}" for key in namekeys )