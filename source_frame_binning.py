from catalog import shenCat
from common.async_tools import generic_unordered_multiprocesser
from common.constants import BASE_SPEC_PATH, SOURCE_SPEC_PATH, join
from common.messaging import done, unfinished_print
from fileio.spec_load_write import async_load, async_write
from spectrum import Spectrum
from spectrum.source_bin_ops import binned_source_to_rest, source_bin

BIN_OUT = join( BASE_SPEC_PATH, "BIN SOURCE" )
REST_OUT = join( BIN_OUT, "REST" )


def bin_wrapper( spec: Spectrum ) -> Spectrum:
    return source_bin( spec )


def rest_wrapper( spec: Spectrum ) -> Spectrum:
    return binned_source_to_rest( spec )

def main( ):

    shenCat.load( )
    names = shenCat.keys( )

    unfinished_print( "Loading source frame speclist... " )
    speclist = async_load( SOURCE_SPEC_PATH, names, '.spec' )
    done( )

    unfinished_print( "Binning source spectra... " )
    generic_unordered_multiprocesser( input_values=speclist, multi_function=bin_wrapper, output_values=speclist )
    done( )

    unfinished_print( "Writing source spectra... " )
    async_write( BIN_OUT, speclist, extention='.bspec' )
    done( )

    unfinished_print( "Shifting to rest frame... " )
    generic_unordered_multiprocesser( input_values=speclist, multi_function=rest_wrapper, output_values=speclist )
    done( )

    unfinished_print( "Writing rest specta... " )
    async_write( REST_OUT, speclist, extention=".rspec" )
    done( )

if __name__ == '__main__':
    main( )
