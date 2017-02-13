"""
# Looking for non-spectral values that correlate the following spectra with 53521-1714-011
#
# 52261-0741-116
# 52353-0507-161
# 53055-1744-387
# 52337-0778-070
# 51910-0461-074
# 53819-2226-431
# 54242-2750-474
# 53115-1382-475
# 52411-0953-343
# 52814-1345-189

These are the EM line matches which come out of the 53521... multispec plot which appear to match best match along
the spectrum (visually).

Results: a few of them fall within uncertainty.  A few are outside of it.

Overall, however, the catalog's black hole mass distribution seems to increase with redshift.

"""
import Gnuplot as gp

from catalog import shenCat

shenCat.load( )
primary = "53521-1714-011"
interest_list = [ '52261-0741-116', '52353-0507-161', '53055-1744-387', '52337-0778-070', '51910-0461-074',
                  '53819-2226-431',
                  '54242-2750-474', '53115-1382-475', '52411-0953-343', '52814-1345-189' ]


def newlist( key ):
    outlist = [ shenCat.subkey( primary, key ) ]
    outlist.extend( [ shenCat.subkey( ns, key ) for ns in interest_list ] )
    return outlist


def propersearch( bh_key: str, all_cat: bool ) -> None:
    bh_key = f"bh_{bh_key}"
    bh_err = f"{bh_key}_err"
    primemass = list( shenCat.subkey( primary, bh_key ) for i in range( 11 ) )
    primemass_low = list( shenCat.subkey( primary, bh_key ) - shenCat.subkey( primary, bh_err ) for i in range( 11 ) )
    primemass_high = list( shenCat.subkey( primary, bh_key ) + shenCat.subkey( primary, bh_err ) for i in range( 11 ) )

    zlist = newlist( 'z' )
    bhmg = newlist( bh_key )
    bhmgerr = newlist( bh_err )

    g = gp.Gnuplot( persist=1 )
    g( 'set grid' )

    alldat = gp.Data( [ shenCat.subkey( ns, 'z' ) for ns in shenCat ],
                      [ shenCat.subkey( ns, bh_key ) for ns in shenCat ], with_="points pt 1 lc 'black'" )

    bhmgdata = gp.Data( zlist, bhmg, bhmgerr, with_="yerrorbars pt 7 ps 2 lc 'royalblue'" )
    prime = gp.Data( zlist, primemass, with_="lines lw 3 lc 'dark-red'" )
    primelow = gp.Data( zlist, primemass_low, with_="lines lw 3 lc 'dark-red'" )
    primehigh = gp.Data( zlist, primemass_high, with_="lines lw 3 lc 'dark-red'" )

    plotlist = [ ]
    if all_cat: plotlist.append( alldat )
    plotlist.extend( [ prime, primelow, primehigh, bhmgdata ] )
    g.plot( *plotlist )


propersearch( "mgii", False )
