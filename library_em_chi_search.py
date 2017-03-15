import logging
from copy import deepcopy

from analysis.chi import chi
from catalog import shenCat
from common.async_tools import generic_unordered_multiprocesser
from common.constants import BASE_PROCESSED_PATH, BETA, GAMMA, HB_RANGE, HG_RANGE, MGII_RANGE, OIII_RANGE, join, linesep
from common.messaging import done, tab_print, unfinished_print
from fileio.list_dict_utils import namestring_dict_writer
from fileio.spec_load_write import async_rspec_scaled, rspecLoader
from fileio.utils import dirCheck
from spectrum import List, Spectrum, Tuple
from spectrum.utils import mutli_scale


def write_shen_results( primary: Spectrum, speclist: List[ Spectrum ] ) -> None:
    filename = f"{ primary.getNS() }.csv"
    nsdict = { }
    for spec in speclist:
        nsdict.update( { spec.getNS( ): shenCat[ spec.getNS( ) ] } )
    namestring_dict_writer( nsdict, join( OUTPATH, "Individual Results" ), filename )


def __single_chi_wrapper( inputV: Tuple[ Spectrum, Spectrum ] ) -> Tuple[ str, float ]:
    pSpec, sSpec = inputV
    return (sSpec.getNS( ), *chi( pSpec, sSpec, old_process=True, get_count=True ))


def single_chi( primary: Spectrum, speclist: List[ Spectrum ], rge: tuple ) -> dict:
    tab_print( f"{ R_DICT[ rge ] } Analysis...", False )

    logging.info( "Performing deepcopy and trim of the primary" )
    p = deepcopy( primary )
    p.trim( wl_range=rge )

    inputV = [ (p, spec) for spec in speclist ]
    results_list = [ ]
    generic_unordered_multiprocesser( inputV, __single_chi_wrapper, results_list )
    results = { }
    for r in results_list:
        try:
            if r[ 1 ] / r[ 2 ] < EM_LINE_MAX:
                results.update( { r[ 0 ]: r[ 1 ] / r[ 2 ] } )
        except ZeroDivisionError:
            ERRSET.add( r[ 1 ] )



    tab_print( f"{ len( results ) }" )
    return results


def single_spec( primary: Spectrum, speclist: List[ Spectrum ] ) -> float:
    print( f"Anaylzing { primary.getNS() }" )

    unfinished_print( "Scaling speclist..." )
    speclist = mutli_scale( primary, speclist )
    done( )
    results = { }
    for rge in R_LIST:
        # Do the chi^2
        results = single_chi( primary, speclist, rge )

        # Reduce the results
        if len( results ) == 0:
            logging.info( "Zero results, returning" )
            return 0
        for i in range( len( speclist ) - 1, -1, -1 ):
            if speclist[ i ].getNS( ) not in results:
                del speclist[ i ]

    # Write the results
    logging.info( "Writing results" )
    write_shen_results( primary, speclist )
    return len( results )


def main_loop( ):
    shenCat.load( )
    namelist = sorted( list( shenCat.keys( ) ) )
    print(f"Limiting chi^2 values to {EM_LINE_MAX}")

    n = len( namelist )

    results = {}
    try:
        with open( join( OUTPATH, "running_count.csv" ), 'r' ) as infile:
            for line in infile:
                if line == "\n":
                    continue
                line.strip()
                line = line.split(',')
                if '\n' in line[ 1 ]:
                    line[ 1 ] = line[ 1 ][:-1]
                results[ line[ 0 ] ] = int( line[ 1 ].strip() )
            try: del line
            except: pass
    except: pass

    for i in range( n ):
        # prime = namelist.pop( i )
        prime = "54115-2493-610";
        namelist.remove( prime )
        if prime in results:
            namelist.insert( i, prime )
            continue
        unfinished_print( f"{i} / {n} Loading spectra from disk..." )
        prime = rspecLoader( prime )
        speclist = async_rspec_scaled( namelist, prime )
        namelist.insert( i, prime )
        done( )

        # do analysis
        count = single_spec( prime, speclist )

        del speclist
        results[ prime.getNS( ) ] = count

        # update count
        with open( join( OUTPATH, "running_count.csv" ), 'a' ) as outfile:
            outfile.write( f"{ prime.getNS() },{ count }" + linesep )
        print( f"{i} / {n} complete." )
        exit()

    # write final counts
    results = [ ( k, v ) for k, v in results.items() ]
    results.sort( key=lambda x: x[ 1 ], reverse=True )
    with open( join( OUTPATH, "final_count.csv" ), 'w' ) as outfile:
        outfile.writelines( [ f"{ x[ 0 ] },{ x[ 1 ] }" + linesep for x in results ] )
    with open( join( OUTPATH, "errors.list" ), 'w' ) as outfile:
        outfile.writelines( [ f"{ns}\n" for ns in ERRSET ] )


EM_LINE_MAX = 0.5
ERRSET = set( )
R_LIST = [ MGII_RANGE, HB_RANGE, OIII_RANGE, HG_RANGE ]
R_DICT = { MGII_RANGE: "MgII", HB_RANGE: f"H{ BETA }", OIII_RANGE: "OIII", HG_RANGE: f"H{ GAMMA }" }
OUTPATH = join( BASE_PROCESSED_PATH, "Analysis", "EM Line Search Testing", f"Chi {EM_LINE_MAX} Old" )

if __name__ == '__main__':
    from common import freeze_support

    freeze_support( )
    dirCheck( OUTPATH )
    main_loop()
