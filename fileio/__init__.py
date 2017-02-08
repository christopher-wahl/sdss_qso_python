from . import spec_load_write

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