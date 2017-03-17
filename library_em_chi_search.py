import logging
from copy import deepcopy

from analysis.chi import chi
from catalog import shenCat
from common.async_tools import generic_unordered_multiprocesser
from common.constants import BASE_PROCESSED_PATH, BETA, CHI_BASE_MAG, CONT_RANGE, GAMMA, HB_RANGE, HG_RANGE, MGII_RANGE, \
    OIII_RANGE, join, linesep
from common.messaging import done, tab_print, unfinished_print
from fileio.list_dict_utils import namestring_dict_writer
from fileio.spec_load_write import async_rspec_scaled, rspecLoader
from fileio.utils import dirCheck
from spectrum import List, Spectrum, Tuple, flux_from_AB


def write_shen_results( primary: Spectrum, speclist: List[ Spectrum ] ) -> None:
    filename = f"{ primary.getNS() }.csv"
    nsdict = { }
    for spec in speclist:
        nsdict.update( { spec.getNS( ): shenCat[ spec.getNS( ) ] } )
    namestring_dict_writer( nsdict, join( OUTPATH, "Individual Results" ), filename )


def __single_chi_wrapper( inputV: Tuple[ Spectrum, Spectrum ] ) -> Tuple[ str, float ]:
    pSpec, sSpec = inputV
    return (sSpec.getNS( ), chi( pSpec, sSpec, old_process=True, skip_2cpy = True ))


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
            if r[ 1 ] < LIMIT_DICT[ rge ]:
                results.update( { r[ 0 ]: r[ 1 ] } )
        except ZeroDivisionError:
            ERRSET.add( r[ 1 ] )

    tab_print( f"{ len( results ) }" )
    return results


def single_spec( primary: Spectrum, speclist: List[ Spectrum ] ) -> float:
    print(
        f"Anaylzing { primary.getNS() }:  AB = { shenCat[ primary.getNS() ][ 'ab' ] }; Z = {shenCat[ primary.getNS() ][ 'z' ]}" )

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
    print( f"Limiting EM Line values to {EM_LINE_MAX} and Continuum to {CONT_MAX}" )

    n = len( namelist )

    results = {}
    try:
        with open( join( OUTPATH, "running_count.csv" ), 'r' ) as infile:
            for line in infile:
                if len(line) < 3:
                    continue
                line.strip()
                line = line.split(',')
                if '\n' in line[ 1 ]:
                    line[ 1 ] = line[ 1 ][:-1]
                results[ line[ 0 ] ] = int( line[ 1 ].strip() )
            try: del line
            except: pass
    except: pass
    print( len( results ) )
    for i in range( n ):
        # prime = namelist.pop( i )
        prime = "54095-2583-381";
        namelist.remove( prime )
        if prime in results:
            namelist.insert( i, prime )
            continue
        unfinished_print( f"{i} / {n} Loading spectra from disk..." )
        prime_spec = rspecLoader( prime )
        prime_spec.scale( scaleflx=flux_from_AB( CHI_BASE_MAG ) )
        speclist = async_rspec_scaled( namelist, prime_spec )
        namelist.insert( i, prime )
        done( )

        # do analysis
        count = single_spec( prime_spec, speclist )

        del speclist
        results[ prime_spec.getNS( ) ] = count

        # update count
        with open( join( OUTPATH, "running_count.csv" ), 'a' ) as outfile:
            outfile.write( f"{ prime_spec.getNS() },{ count }" + linesep )
        print( f"{i} / {n} complete." )
        exit()

    # write final counts
    results = [ ( k, v ) for k, v in results.items() ]
    results.sort( key=lambda x: x[ 1 ], reverse=True )
    with open( join( OUTPATH, "final_count.csv" ), 'w' ) as outfile:
        outfile.writelines( [ f"{ x[ 0 ] },{ x[ 1 ] }" + linesep for x in results ] )
    if len( ERRSET ) > 0:
        with open( join( OUTPATH, "errors.list" ), 'w' ) as outfile:
            outfile.writelines( [ f"{ns}\n" for ns in ERRSET ] )


EM_LINE_MAX = 10
CONT_MAX = 100
ERRSET = set( )

R_LIST = [ MGII_RANGE, HB_RANGE, OIII_RANGE, CONT_RANGE ]  # , OIII_RANGE, HG_RANGE ]
R_DICT = { MGII_RANGE: "MgII", HB_RANGE: f"H{ BETA }", OIII_RANGE: "OIII", HG_RANGE: f"H{ GAMMA }",
           CONT_RANGE: "Continuum" }
LIMIT_DICT = { MGII_RANGE: EM_LINE_MAX, HB_RANGE: EM_LINE_MAX, OIII_RANGE: EM_LINE_MAX, HG_RANGE: EM_LINE_MAX,
               CONT_RANGE: CONT_MAX }
OUTPATH = join( BASE_PROCESSED_PATH, "Analysis", "EM + C CHI20 Search", f"EM {EM_LINE_MAX} CONT {CONT_MAX} Old" )

if __name__ == '__main__':
    from common import freeze_support

    freeze_support( )
    dirCheck( OUTPATH )
    try:
        main_loop()
    except KeyboardInterrupt:
        exit()
