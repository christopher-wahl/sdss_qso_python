from analysis.pipeline import redshift_ab_pipeline
from catalog import shenCat
from common.constants import BASE_PLOT_PATH, join, linesep


def main( ):
    shenCat.load( )
    nameslist = list( sorted( shenCat.keys( ) ) )
    outpath = join( BASE_PLOT_PATH, "all_evos" )
    n = len( nameslist )
    counts = [ ]
    for i in range( n ):
        ns = nameslist.pop( i )
        pipe = redshift_ab_pipeline( ns, ns_of_interest=nameslist )
        r = pipe.reduce_results( 0.5 )
        counts.append( len( r ) )
        # ab_z_plot( outpath, f"{ns}.pdf", ns, list( r.keys( ) ), plotTitle=f"{ns} Assumed Effect", n_sigma=0.5 )
        print( f"{i}/{n}" )
        nameslist.insert( i, ns )
    with open( join( BASE_PLOT_PATH, "count.txt" ), 'w' ) as outfile:
        for c in counts:
            outfile.write( str( c ) + linesep )
    print( "Done" )

if __name__ == '__main__':
    from common import freeze_support

    freeze_support( )
    main( )
