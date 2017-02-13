from astropy.io.fits import getdata, getheader

from catalog import shenCat
from common.constants import BASE_PROCESSED_PATH, join

"""
Working notes:

The RAW shencatalog.FITS file pulls the following key indecies

128: -> LOGBH_HB_VP06
129: -> LOGBH_HB_VP06_ERR

134: -> LOGBH_MGII_S10
135: -> LOGBH_MGII_S10_ERR

4: -> PLATE
5: -> FIBER
6: -> MJD

Namestring format: MJD->PLATE->FIBER: 6-4-5
3: O.G. Redshift
142: Z_HW
"""

s_source = "/media/christopher/Research/Source/shen/dr7_bh_May_2011.fits"


def isolate_namestring( dp: list ) -> str:
    return "%05i-%04i-%03i" % (dp[ 6 ], dp[ 4 ], dp[ 5 ])


def write_raw_keys( ):
    header = getheader( s_source, 1 )
    shenCat.load( )

    keys = list( header.keys( ) )
    for i in range( len( keys ) ):
        k = keys[ i ]
        print( f"{i - 14 }: {k} -> {header[ k ]}" )


def form_raw_shen( ):
    source = "/media/christopher/Research/Source/shen/dr7_bh_May_2011.fits"
    header = getheader( source, 1 )
    data = getdata( source )
    shenCat.load( )

    keys = list( header.keys( ) )
    """for i in range( len( keys ) ):
        k = keys[ i ]
        print( f"{i - 14 }: {k} -> {header[ k ]}")
    """
    dumpdict = { }
    for d in data:
        ns = isolate_namestring( d )
        if ns in shenCat:
            dumpdict[ ns ] = list( d )
            shenCat.pop( ns )

    import pickle
    from common.constants import BASE_PROCESSED_PATH, join
    pickle.dump( dumpdict, open( join( BASE_PROCESSED_PATH, 'shen_raw.bin' ), 'wb' ) )


def add_bh_masses( ):
    import pickle
    shenCat.load( )
    ddict = pickle.load( open( join( BASE_PROCESSED_PATH, 'shen_raw.bin' ), 'rb' ) )
    for ns in shenCat:
        shenCat[ ns ][ 'bh_mgii_err' ] = ddict[ ns ][ 135 ]
        shenCat[ ns ][ 'bh_hb_err' ] = ddict[ ns ][ 129 ]
        print( shenCat[ ns ] )

    pickle.dump( shenCat, open( join( BASE_PROCESSED_PATH, 'shenCat.bin' ), 'wb' ) )
    # shenCat.export_text()


def do_full_shen_distribution( bh_key=128 ) -> None:
    data = getdata( s_source )
    z = [ ]
    bh = [ ]

    z_key = 3
    i = 0
    n = len( data )
    for dp in data:
        i += 1
        if i % 1000 == 0:
            print( f"{i} / {n}" )

        z_ = dp[ z_key ]
        bh_ = dp[ bh_key ]
        if z_ == 0 or bh_ == 0:
            continue
        z.append( dp[ z_key ] )
        bh.append( dp[ bh_key ] )

    import Gnuplot
    g = Gnuplot.Gnuplot( )
    g( 'set grid ' )
    plotdata = Gnuplot.Data( z, bh, with_="points pt 1 lc \"black\"" )
    g( 'set terminal pdf enhanced color size 9,6' )

    from common.constants import BASE_PLOT_PATH
    g( f'set output "{join( BASE_PLOT_PATH, "catalog_z.pdf" )}"' )
    g.plot( plotdata )
    g( 'set output' )


if __name__ == '__main__':
    do_full_shen_distribution( )
