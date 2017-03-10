import logging
import pickle
from csv import DictWriter

from astropy.io.fits import getdata, getheader

from common.constants import BASE_PROCESSED_PATH, join

binfile = join( BASE_PROCESSED_PATH, "shenbyte.bin" )


def print_shen_values( ):
    source_file = "/media/christopher/Research/Source/shen/dr7_bh_May_2011.fits"
    header = getheader( source_file, 1 )
    data = getdata( source_file )
    h_keys = [ h for h in header ]
    for i in range( len( h_keys ) - 1, 170, -1 ):
        h_keys.pop( i )
    for i in range( 13, -1, -1 ):
        h_keys.pop( i )
    i = 0
    n = len( data )
    fd = [ header[ h ] for h in h_keys ]
    del h_keys

    with open( "/home/christopher/shencsv.csv", "w" ) as outfile:
        writer = DictWriter( outfile, fieldnames=fd )
        writer.writeheader( )
        for dp in data:
            dd = { }
            for f in fd:
                dd[ f ] = dp[ f ]
            writer.writerow( dd )
            i += 1
            if (i % 1000 == 0):
                logging.info( f"{i}/{n}" )
    logging.info( "Done" )

    # data = getdata( source_file, 2 )
    # print( type( data ) )


def getfds( ) -> list:
    source_file = "/media/christopher/Research/Source/shen/dr7_bh_May_2011.fits"
    header = getheader( source_file, 1 )
    data = getdata( source_file )
    h_keys = [ h for h in header ]
    for i in range( len( h_keys ) - 1, 170, -1 ):
        h_keys.pop( i )
    for i in range( 13, -1, -1 ):
        h_keys.pop( i )
    i = 0
    n = len( data )
    return [ header[ h ] for h in h_keys ]


def write_shen_byte( ):
    source_file = "/media/christopher/Research/Source/shen/dr7_bh_May_2011.fits"
    header = getheader( source_file, 1 )
    data = getdata( source_file )
    h_keys = [ h for h in header ]
    for i in range( len( h_keys ) - 1, 170, -1 ):
        h_keys.pop( i )
    for i in range( 13, -1, -1 ):
        h_keys.pop( i )
    i = 0
    n = len( data )
    fd = [ header[ h ] for h in h_keys ]
    del h_keys

    bigdict = { }
    from common.constants import BASE_PROCESSED_PATH, join
    with open( join( BASE_PROCESSED_PATH, "shebyte.bin" ), 'wb' ) as outfile:
        pickle.dump( bigdict, outfile )

    PLATE = fd.index( "PLATE" )
    MJD = fd.index( "MJD" )
    FIBER = fd.index( "FIBER" )

    def makename( dp ) -> str:
        return "%05i-%04i-%03i" % (dp[ MJD ], dp[ PLATE ], dp[ FIBER ])

    i, n = 0, len( data )
    for dp in data:
        dd = { }
        for f in fd: dd[ f ] = dp[ f ]
        bigdict[ makename( dp ) ] = dd
        i += 1
        if i % 5000 == 0: logging.info( f"{i}/{n}" )
    logging.info( "Processed.  Writing." )
    del data

    with open( join( BASE_PROCESSED_PATH, "shebyte.bin" ), 'wb' ) as outfile:
        pickle.dump( bigdict, outfile )
    logging.info( "Written." )


def write_x_y( outpath, x, y, subkey=None ):
    fd = getfds( )
    k0 = fd.index( x )
    k1 = fd.index( y )
    with open( binfile, 'rb' ) as infile:
        d = pickle.load( infile )
    logging.info( "Binary loaded" )
    with open( outpath, 'w' ) as outfile:
        outfile.write( f"{x},{y}\n" )
        for dp in d:
            z = d[ dp ][ x ]
            g = d[ dp ][ y ][ subkey ]
            if not (0.46 > z or 0.82 < z or 19 < g):
                continue
            if subkey is None:
                outfile.write( f"{ d[ dp ][ x ] },{ d[ dp ][ y ] }\n" )
            else:
                outfile.write( f"{ d[ dp ][ x ] },{ d[ dp ][ y ][ subkey ] }\n" )
    logging.info( f"Writing {outpath} complete" )


if __name__ == '__main__':
    logging.basicConfig( level=logging.INFO )
    logging.info( "Try again..." )
    # print_shen_values()
    # write_shen_byte()
    # print( getfds() )
    write_x_y( join( BASE_PROCESSED_PATH, "zg_exclude.csv" ), 'Z_HW', 'UGRIZ', 2 )
