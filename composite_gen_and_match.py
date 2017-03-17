from numpy import log10
from scipy.optimize import curve_fit

from analysis.chi import chi
from catalog import shenCat
from common.async_tools import generic_unordered_multiprocesser
from common.constants import CONT_RANGE, HB_RANGE, HG_RANGE, MGII_RANGE, OIII_RANGE, RANGE_STRING_DICT
from common.messaging import done, unfinished_print
from fileio.list_dict_utils import namestring_dict_reader, namestring_dict_writer
from fileio.spec_load_write import async_rspec, async_rspec_scaled, join, rspecLoader, text_write, write
from spectrum import Iterable, List, Spectrum, Tuple
from spectrum.utils import compose_speclist, flux_from_AB, reduce_speclist
from tools.list_dict import sort_list_by_shen_key
from tools.plot import ab_z_plot, four_by_four_multiplot, spectrum_plot

EM_LINE_MAX = 10
CONTNUUM_MAX = 50
MATCH_SCHEMA = [ MGII_RANGE, HB_RANGE, CONT_RANGE ]
FITTING_FUNC = log10
OLD_PROCESS = True
LIMIT_DICT = { MGII_RANGE: EM_LINE_MAX, HB_RANGE: EM_LINE_MAX, HG_RANGE: EM_LINE_MAX, OIII_RANGE: EM_LINE_MAX,
               CONT_RANGE: CONTNUUM_MAX }
SOURCE_DIR = "/media/christopher/Research/Processed/Analysis/EM + C Search/EM 20 CONT 200 Old/Individual Results"
CDIR = "/media/christopher/Research/Processed/Analysis/EM + C Search/EM 20 CONT 200 Old/Composites"


def __chi_wrapper( inputV ):
    prime, spec = inputV
    return (spec.getNS( ), chi( prime, spec, old_process=OLD_PROCESS ))


def anaylsis( composite: Spectrum, speclist: List[ Spectrum ], rge: Tuple[ float, float ] ) -> dict:
    def _outfilter( dp ):
        return dp[ 1 ] < LIMIT_DICT[ rge ]

    composite = composite.cpy( )
    composite.trim( wl_range=rge )
    out = [ ]
    generic_unordered_multiprocesser( [ (composite, spec) for spec in speclist ], __chi_wrapper, out )
    out = filter( _outfilter, out )
    return dict( out )


def match_scheme( composite: Spectrum, range_scheme: Iterable[ Tuple[ float, float ] ] = MATCH_SCHEMA,
                  ns_list: Iterable = shenCat.keys( ) ) -> dict:
    unfinished_print( "Loading scaled catalog..." )
    composite.scale( scaleflx=flux_from_AB( 20 ) )
    speclist = async_rspec_scaled( ns_list, composite )
    done( )
    results = { }
    for rge in range_scheme:
        unfinished_print( f"{RANGE_STRING_DICT[ rge ]} analysis..." )
        results = anaylsis( composite, speclist, rge )
        if len( results ) == 0:
            return { }
        reduce_speclist( results.keys( ), speclist )
        print( len( speclist ) )

    return results


def fit_func( x, a, b ):
    return a * FITTING_FUNC( x ) + b


def fit_log( data_dict: dict ):
    datax, datay = [ ], [ ]
    for dp in data_dict:
        datax.append( shenCat.subkey( dp, 'z' ) )
        datay.append( shenCat.subkey( dp, 'ab' ) )
    coeff, pcov = curve_fit( fit_func, datax, datay )
    return coeff[ 0 ], coeff[ 1 ]


def main( base_ns: str ):
    shenCat.load( )
    BASE_PATH = join( CDIR, base_ns )

    unfinished_print( f"Loading base spectrum {base_ns}..." )
    base = rspecLoader( base_ns )
    done( )

    unfinished_print( "Loading base matches DAT..." )
    source_dict = namestring_dict_reader( SOURCE_DIR, f"{base_ns}.csv" )
    done( )

    # Fit AB( z ) function, determine scale values
    unfinished_print( "Fitting AB magnitudes as a function of redshift... " )
    a, b = fit_log( source_dict )
    print( f"Fit function: {a} {FITTING_FUNC.__name__}( z ) + {b}" )
    scaleAB = fit_func( 0.46, a, b )
    scaleflx = flux_from_AB( scaleAB )
    print( f"Scale values:  AB( z = 0.46 ) = {scaleAB};   Flux Density = {scaleflx}" )

    # Do Source AB v Z plot
    unfinished_print( "Plotting SOURCE AB v Z..." )
    ab_z_plot( BASE_PATH, "SOURCE AB v Z.pdf", base_ns, source_dict, f"SOURCE DATA Composite {base_ns}",
               rs_fit_func=lambda x: fit_func( x, a, b ),
               rs_fit_title=f"Fit: %0.2f {FITTING_FUNC.__name__}( z ) + %0.2f" % (a, b) )
    done( )

    # Scale all spectra to z = 0.46 on fit function
    unfinished_print( "Loading scaled matches..." )
    speclist = async_rspec_scaled( [ *source_dict.keys( ) ], base )
    done( )

    # Drop a 4x4 plot of these
    four_by_four_multiplot( base, speclist, BASE_PATH, "Source Multiplot.pdf",
                            f"Matches to {base_ns} EM 20 CONT 200 Old" )

    unfinished_print( "Generating composite spectrum..." )
    composite = compose_speclist( speclist, f"Composite Base {base_ns}" )
    composite.setRS( shenCat[ base_ns ][ 'z' ] )
    del speclist
    done( )

    unfinished_print( "Writing composite data and spectrum plot..." )
    text_write( composite, BASE_PATH, "composite.text_rspec" )
    write( composite, BASE_PATH, "composite.rspec" )
    spectrum_plot( composite, BASE_PATH, "Composite" )
    done( )

    # Run composite matching scheme
    #       Running:    MgII = HB = 20
    #                   Continuum = 200
    unfinished_print( f"Running match scheme (EM: {EM_LINE_MAX}, CONT: {CONTNUUM_MAX})...\n" )
    results = match_scheme( composite )
    done( )

    # get new fit from results
    unfinished_print( "Fitting new results... " )
    a, b = fit_log( results )
    print( f"New fit: {a} {FITTING_FUNC.__name__}( z ) + {b}" )

    # Plot AB v Z of results
    unfinished_print( "Writing and plotting match results..." )
    first = list( results.keys( ) )[ 0 ]
    composite.scale( spec=rspecLoader( first ) )
    composite.setRS( shenCat[ first ][ 'z' ] )
    for ns in results:
        results[ ns ] = shenCat[ ns ]
    namestring_dict_writer( results, BASE_PATH, "Composite Matches.dat" )
    ab_z_plot( BASE_PATH, "Composite AB v Z sigma 1.pdf", composite, results, n_sigma=1,
               rs_fit_func=lambda x: fit_func( x, a, b ),
               rs_fit_title=f"Fit: %0.2f {FITTING_FUNC.__name__}( z ) + %0.2f" % (a, b) )
    ab_z_plot( BASE_PATH, "Composite AB v Z sigma 2.pdf", composite, results, n_sigma=2,
               rs_fit_func=lambda x: fit_func( x, a, b ),
               rs_fit_title=f"Fit: %0.2f {FITTING_FUNC.__name__}( z ) + %0.2f" % (a, b) )
    # Plot 4x4 results
    speclist = sort_list_by_shen_key( async_rspec_scaled( results.keys( ), composite ) )
    four_by_four_multiplot( composite, speclist, BASE_PATH, "Composite Multiplot.pdf", composite.getNS( ) )
    done( )


def test( ):
    import numpy
    numpy.seterr( all="raise" )
    shenCat.load( )
    speclist = async_rspec( shenCat.keys( ) )
    for spec in speclist:
        ns = spec.getNS( )
        ab = spec.magAB( )
        try:
            aberr = spec.abErr( )
        except FloatingPointError:
            print( spec )
            print( spec.abErr( ) )
            exit( )
        shenCat[ ns ][ 'ab' ] = ab
        shenCat[ ns ][ 'ab_err' ] = aberr
    exit( )


def redo_comp( base_ns: str ):
    from fileio.spec_load_write import load

    BASE_PATH = join( CDIR, base_ns )
    composite = load( BASE_PATH, "composite.rspec" )
    compdict = namestring_dict_reader( BASE_PATH, "Composite Matches.dat" )
    firstmatch = rspecLoader( list( compdict.keys( ) )[ 0 ] )
    composite.scale( scaleflx=flux_from_AB( 20 ) )
    # composite.setRS( shenCat.subkey( firstmatch.getNS(), 'z' ) )
    speclist = async_rspec_scaled( list( compdict.keys( ) ), flux_from_AB( 20 ) )
    for spec in speclist:
        print( spec.magAB( ) )
    print( f"Composite AB Magnitude: {composite.magAB()}" )
    unfinished_print( f"Running match scheme (EM: {EM_LINE_MAX}, CONT: {CONTNUUM_MAX})...\n" )
    results = match_scheme( composite, ns_list=compdict.keys( ) )
    done( )

    # get new fit from results
    unfinished_print( "Fitting new results... " )
    a, b = fit_log( results )
    print( f"New fit: {a} {FITTING_FUNC.__name__}( z ) + {b}" )

    # Plot AB v Z of results
    unfinished_print( "Writing and plotting match results..." )
    for ns in results:
        results[ ns ] = shenCat[ ns ]
    namestring_dict_writer( results, BASE_PATH, "Composite Matches - redo.dat" )
    ab_z_plot( BASE_PATH, "Composite AB v Z sigma 1 - redo.pdf", composite, results, n_sigma=1,
               rs_fit_func=lambda x: fit_func( x, a, b ),
               rs_fit_title=f"Fit: %0.2f {FITTING_FUNC.__name__}( z ) + %0.2f" % (a, b) )
    ab_z_plot( BASE_PATH, "Composite AB v Z sigma 2 - redo.pdf", composite, results, n_sigma=2,
               rs_fit_func=lambda x: fit_func( x, a, b ),
               rs_fit_title=f"Fit: %0.2f {FITTING_FUNC.__name__}( z ) + %0.2f" % (a, b) )
    # Plot 4x4 results
    speclist = sort_list_by_shen_key( async_rspec_scaled( results.keys( ), composite ) )
    four_by_four_multiplot( composite, speclist, BASE_PATH, "Composite Multiplot - redo.pdf", composite.getNS( ) )
    done( )
    exit( )


#redo_comp( "51821-0408-552" )

if __name__ == '__main__':
    from common import freeze_support

    freeze_support( )
    try:
        main( "51821-0408-552" )
    except KeyboardInterrupt:
        print( "Got BREAK command. Quitting..." )
    finally:
        print( "Process Complete." )
