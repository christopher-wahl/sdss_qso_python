import logging

from catalog import shenCat
from common.constants import BASE_PLOT_PATH, BASE_PROCESSED_PATH
from fileio.list_dict_utils import namestring_dict_reader
from fileio.spec_load_write import async_rspec, join, rspecLoader
from library_em_chi_search import analyze
from spectrum.utils import compose_speclist, scale_enmasse
from tools.plot import ab_z_plot, four_by_four_multiplot


def main( ns: str = "54115-2493-610", n: float = 3, chi: float = 20, mchi=20 ) -> None:
    FOLDER_STR = f"Sigma {n} - Max {chi}"
    BASE_INTEREST = join( BASE_PROCESSED_PATH, "Chi Matching", "EM Lines" )
    PROGRAM_PATH = join( BASE_INTEREST, FOLDER_STR )
    INDI_PATH = join( PROGRAM_PATH, "Individual Matches" )
    PLOT_PATH = join( BASE_PLOT_PATH, "EM Line Matching", "Composites" )

    shenCat.load( )
    rdict = namestring_dict_reader( INDI_PATH, f'{ns}.csv', has_header=True )
    logging.info( "Results loaded" )

    primary = rspecLoader( ns )
    speclist = async_rspec( rdict.keys( ) )
    speclist = scale_enmasse( primary, speclist )

    logging.info( "Speclist loaded" )

    from fileio.spec_load_write import text_write

    cspec = compose_speclist( speclist, f"{ns} Chi 20 Results" )
    logging.info( "CSpec generated" )
    outpath = "/home/christopher/Desktop/composite/"
    text_write( cspec, outpath, "composite.spec" )
    for spec in speclist:
        text_write( spec, outpath, f"{spec.getNS()}.rspec" )
    logging.info( "Specs written" )
    exit( )

    newd = namestring_dict_reader( PLOT_PATH, f"{cspec.getNS()}.csv" )
    cspec.setNS( f"{ns} Chi {mchi} Results" )

    r = analyze( cspec.cpy( ), newd.keys( ), 1, PLOT_PATH, MAX=mchi, getDict=True )
    ab_z_plot( PLOT_PATH, f"{cspec.getNS()} {mchi}.pdf", rspecLoader( ns ), list( r ) )
    logging.info( "ab plot" )
    speclist = scale_enmasse( cspec, async_rspec( list( r ) ) )
    four_by_four_multiplot( cspec, speclist, path=PLOT_PATH, filename=f"{cspec.getNS()} {mchi} Multi.pdf" )
    logging.info( "4x4" )



if __name__ == '__main__':
    if __debug__:
        logging.basicConfig( level=logging.INFO )
    main( mchi=20 )
