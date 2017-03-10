from analysis.pipeline import redshift_ab_pipeline
from catalog import shenCat
from common.constants import BASE_PLOT_PATH, join
from tools.plot import ab_z_plot


def main( ):
    shenCat.load( )
    nameslist = list( sorted( shenCat.keys( ) ) )
    outpath = join( BASE_PLOT_PATH, "all_evos" )
    n = len( nameslist )
    for i in range( n ):
        ns = nameslist.pop( i )
        pipe = redshift_ab_pipeline( ns, ns_of_interest=nameslist )
        r = pipe.reduce_results( 0.5 )
        if len( r ) == 0:
            continue
        ab_z_plot( outpath, f"{ns}.pdf", ns, list( r.keys( ) ), plotTitle=f"{ns} Assumed Effect", n_sigma=0.5 )
        print( f"{i}/{n}" )
        nameslist.insert( i, ns )


if __name__ == '__main__':
    from common import freeze_support

    freeze_support( )
    main( )
