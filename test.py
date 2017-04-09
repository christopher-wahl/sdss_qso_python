from fileio.list_dict_utils import namestring_dict_reader

inpath, indat = "/home/christopher/Desktop/103/", "/home/christopher/Desktop/103/53327-1928-103.csv"
dat = namestring_dict_reader( inpath, indat )

dlist = [ ]
for k, v in dat.items():
    dlist.append( (k, v[ 'z' ], v[ 'z_err' ], v[ 'ab' ], v[ 'ab_err' ], v[ 'bh_hb' ], v[ 'bh_hb_err' ], v[ 'bh_mgii' ],
                   v[ 'bh_mgii_err' ]) )
dlist.sort( key=lambda x: x[ 1 ] )


def find_digit( s ):
    s = str( s )
    for i in range( len( s ) ):
        if s[ i ] != "0" and s[ i ] != ".":
            return i + 1
    return -1


for d in dlist:
    s = d[ 0 ] + " & "
    zlen = find_digit( d[ 2 ] )
    z = str( d[ 1 ] )[ :zlen + 1 ]
    zerr = str( d[ 2 ] )[ :zlen + 1 ]
    s += f"\( {z} \pm {zerr} \) & "

    ablen = find_digit( d[ 4 ] )
    ab = str( d[ 3 ] )[ :ablen + 1 ]
    aberr = str( d[ 4 ] )[ :ablen + 1 ]
    s += f"\( {ab} \pm {aberr} \) & "

    hblen = find_digit( d[ 6 ] )
    hb = str( d[ 5 ] )[ :hblen + 1 ]
    hberr = str( d[ 6 ] )[ :hblen + 1 ]
    s += f"\( {hb} \pm {hberr} \) & "

    mglen = find_digit( d[ 8 ] )
    mgii = str( d[ 7 ] )[ :mglen + 1 ]
    mgiierr = str( d[ 8 ] )[ :mglen + 1 ]
    s += f"\( {mgii} \pm {mgiierr} \) \\\\"

    print( s )
