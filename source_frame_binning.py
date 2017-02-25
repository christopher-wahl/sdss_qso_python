from catalog import shenCat
from common.async_tools import generic_unordered_multiprocesser
from common.constants import BASE_PROCESSED_PATH, BASE_SPEC_PATH, BINNED_SPEC_PATH, REST_SPEC_PATH, SOURCE_SPEC_PATH, \
    join
from common.messaging import done, unfinished_print
from fileio.spec_load_write import async_load, async_write, sspecLoader, text_write, write
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

def test():
    shenCat.load()
    TEXT_BACKUP = join( BASE_PROCESSED_PATH, "Spec", "TEXT_BACKUP", "BINNED_SOURCE" )
    i = 1
    for ns in shenCat:
        spec = sspecLoader( ns )
        bspec = source_bin( spec )
        rspec = binned_source_to_rest( bspec )

        write( bspec, BINNED_SPEC_PATH, f"{ns}.bspec" )
        write( rspec, REST_SPEC_PATH, f"{ns}.rspec" )

        text_write( bspec, TEXT_BACKUP, f"{ns}.bspec")
        text_write( rspec, join( TEXT_BACKUP, "REST" ), f"{ns}.rspec")
        print( f"{i}: {ns}" )
        i += 1



if __name__ == '__main__':
    #main( )
    test()
