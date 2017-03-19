from analysis.chi import multi_chi_analysis
from catalog import shenCat
from common.constants import BASE_ANALYSIS_PATH, CHI_BASE_MAG, CONT_RANGE, HG_RANGE, MGII_RANGE
from fileio.spec_load_write import async_rspec_scaled, load
from fileio.utils import join
from spectrum import flux_from_AB
from tools.plot import ab_z_plot, four_by_four_multiplot

EM_LINE = 7
BASE_PATH = join( BASE_ANALYSIS_PATH, "EM 15 CONT 100 Old" )
SOURCE_DIR = join( BASE_PATH, "Individual Results" )
CDIR = join( BASE_PATH, "Composites" )
sourcepath, sourcefile = "/media/christopher/Research/Processed/Analysis/EM 15 CONT 100 Old/Composites/53818-2440-539/", "composite.rspec"


def main( ns: str ) -> None:
    composite = load( sourcepath, sourcefile )
    composite.scale( scaleflx=flux_from_AB( CHI_BASE_MAG ) )
    speclist = async_rspec_scaled( shenCat.keys( ), composite )
    chilist = [ ]
    c2 = composite.cpy( )
    c2.trim( wl_range=HG_RANGE )
    chid = multi_chi_analysis( c2, speclist, skip_2cpy=True )
    chilist = [ (k, v) for k, v in chid.items( ) ]
    chilist.sort( key=lambda x: x[ 1 ], reverse=True )
    chilist = list( filter( lambda x: x[ 1 ] < 5, chilist ) )
    print( f"HG Range done: {len(chilist)}" )

    c2 = composite.cpy( )
    c2.trim( wl_range=MGII_RANGE )
    speclist = async_rspec_scaled( [ x[ 0 ] for x in chilist ], composite )
    chid = multi_chi_analysis( c2, speclist, skip_2cpy=True )
    chilist = [ (k, v) for k, v in chid.items( ) ]
    chilist.sort( key=lambda x: x[ 1 ], reverse=True )
    chilist = list( filter( lambda x: x[ 1 ] < EM_LINE, chilist ) )
    print( f"MGII Range done: {len(chilist)}" )

    c2 = composite.cpy( )
    c2.trim( wl_range=CONT_RANGE )
    speclist = async_rspec_scaled( [ x[ 0 ] for x in chilist ], composite )
    chid = multi_chi_analysis( c2, speclist, skip_2cpy=True )
    chilist = [ (k, v) for k, v in chid.items( ) ]
    chilist.sort( key=lambda x: x[ 1 ], reverse=True )
    chilist = list( filter( lambda x: x[ 1 ] < EM_LINE, chilist ) )
    print( f"MGII Range done: {len(chilist)}" )

    speclist = async_rspec_scaled( [ x[ 0 ] for x in chilist ], composite )
    ab_z_plot( sourcepath, "test.pdf", None, speclist )
    four_by_four_multiplot( composite, speclist, sourcepath, "testmulti.pdf" )


if __name__ == '__main__':
    main( None )
