from analysis.pipeline import speclist_analysis_pipeline
from catalog import shenCat
from common.constants import BASE_PLOT_PATH, CONT_RANGE, HB_RANGE, HG_RANGE, MGII_RANGE, OIII_RANGE, join, linesep
from fileio.list_dict_utils import namestring_dict_writer
from fileio.spec_load_write import async_bspec, bspecLoader
from spectrum import List, Spectrum, scale_enmasse
from tools.list_dict import sort_list_by_shen_key
from tools.plot import ab_z_plot, four_by_four_multiplot


def reduced_chi( primary: Spectrum, secondary: Spectrum, doScale: bool = False, skipCopy: bool = False,
                 wl_low: float = None, wl_high: float = None ) -> float:
    if not skipCopy:
        primary = primary.cpy( )
        secondary = secondary.cpy( )

    if doScale:
        secondary.scale( spec=primary )
    if wl_low:
        primary.trim( wlLow=wl_low )
        secondary.trim( wlLow=wl_low )
    if wl_high:
        primary.trim( wlHigh=wl_high )
        secondary.trim( wlHigh=wl_high )

    secondary.alignToSpec( primary )
    n = len( secondary )
    if n == 0:
        return -1
    return sum( [ pow( primary.getFlux( wl ) - secondary.getFlux( wl ), 2 ) / primary.getFlux( wl ) for wl in
                  primary ] ) / n


def reduced_chi_wrapper( input_value: tuple ) -> dict:
    primary, seconday, wl_range = input_value
    return { seconday.getNS( ): reduced_chi( primary, seconday, True, False, wl_range[ 0 ], wl_range[ 1 ] ) }


def cut_speclist( speclist: List[ Spectrum ], results_dict: dict ):
    for i in range( len( speclist ) - 1, -1, -1 ):
        if speclist[ i ].getNS( ) not in results_dict:
            del speclist[ i ]


def single( pns: str, names: List[ str ] ) -> dict:
    outpath = join( BASE_PLOT_PATH, 'Ave Error Search', pns )
    shenCat.load( )

    pspec = bspecLoader( pns )
    print( "Loading speclist...", end="" )
    speclist = async_bspec( names )
    print( "Done", end=linesep )

    err = pspec.aveErr( wl_range=MGII_RANGE ) / 2
    print( f"Building the MGII anaylsis pipeline with maximum value {err}...", end="" )
    input_values = [ (pspec, spec, MGII_RANGE) for spec in speclist ]
    chi_pipe = speclist_analysis_pipeline( pspec, speclist, reduced_chi_wrapper, (0, err), input_values )
    print( "Done", end=linesep )

    print( "Running MGII pipeline.... ", end="" )
    chi_pipe.do_analysis( )
    print( "Reducing results.... ", end="" )
    r = chi_pipe.reduce_results( )
    cut_speclist( speclist, r )
    print( f"{len( r )} remain.", end=linesep )

    if len( speclist ) == 0:
        return { pns: 0 }

    ab_z_plot( path=outpath, filename="MGII.pdf", primary=pns, points=r, plotTitle=f"{pns}" )

    err = pspec.aveErr( wl_range=HB_RANGE ) / 2
    print( f"Building the HB anaylsis pipeline with maximum value {err}...", end="" )
    input_values = [ (pspec, spec, HB_RANGE) for spec in speclist ]
    chi_pipe = speclist_analysis_pipeline( pspec, speclist, reduced_chi_wrapper,
                                           (0, err), input_values )
    print( "Done", end=linesep )

    print( "Running HB pipeline.... ", end="" )
    chi_pipe.do_analysis( )
    print( "Reducing results.... ", end="" )
    r = chi_pipe.reduce_results( )
    cut_speclist( speclist, r )
    print( f"{len( r )} remain.", end=linesep )

    if len( speclist ) == 0:
        return { pns: 0 }

    ab_z_plot( path=outpath, filename="MGII and HB.pdf", primary=pns, points=r, plotTitle=f"{pns}" )

    err = pspec.aveErr( wl_range=OIII_RANGE ) / 2
    print( f"Building the OIII anaylsis pipeline with maximum value {err}...", end="" )
    input_values = [ (pspec, spec, OIII_RANGE) for spec in speclist ]
    chi_pipe = speclist_analysis_pipeline( pspec, speclist, reduced_chi_wrapper,
                                           (0, err), input_values )
    print( "Done", end=linesep )

    print( "Running OIII pipeline.... ", end="" )
    chi_pipe.do_analysis( )
    print( "Reducing results.... ", end="" )
    r = chi_pipe.reduce_results( )
    cut_speclist( speclist, r )
    print( f"{len( r )} remain.", end=linesep )

    if len( speclist ) == 0:
        return { pns: 0 }

    ab_z_plot( path=outpath, filename="MGII, HB and OIII.pdf", primary=pns, points=r, plotTitle=f"{pns}" )

    err = pspec.aveErr( wl_range=HG_RANGE ) / 2
    print( f"Building the HG anaylsis pipeline with maximum value {err}...", end="" )
    input_values = [ (pspec, spec, HG_RANGE) for spec in speclist ]
    chi_pipe = speclist_analysis_pipeline( pspec, speclist, reduced_chi_wrapper,
                                           (0, err), input_values )
    print( "Done", end=linesep )

    print( "Running HG pipeline.... ", end="" )
    chi_pipe.do_analysis( )
    print( "Reducing results.... ", end="" )
    r = chi_pipe.reduce_results( )
    cut_speclist( speclist, r )
    print( f"{len( r )} remain.", end=linesep )

    if len( speclist ) == 0:
        return { pns: 0 }

    ab_z_plot( path=outpath, filename="MGII, HB and OIII and HG.pdf", primary=pns, points=r, plotTitle=f"{pns}" )

    err = pspec.aveErr( wl_range=CONT_RANGE ) / 2
    print( f"Building the Continuum anaylsis pipeline with maximum value {err}...", end="" )
    input_values = [ (pspec, spec, CONT_RANGE) for spec in speclist ]
    chi_pipe = speclist_analysis_pipeline( pspec, speclist, reduced_chi_wrapper,
                                           (0, err), input_values )
    print( "Done", end=linesep )

    print( "Running Continuum pipeline.... ", end="" )
    chi_pipe.do_analysis( )
    print( "Reducing results.... ", end="" )
    r = chi_pipe.reduce_results( )
    cut_speclist( speclist, r )
    print( f"{len( r )} remain.", end=linesep )

    if len( speclist ) == 0:
        return { pns: 0 }

    ab_z_plot( path=outpath, filename="MGII, HB and OIII and HG and Continuum.pdf", primary=pns, points=r,
               plotTitle=f"{pns}" )

    print( "Scaling speclist...", end="" )
    speclist = scale_enmasse( pspec, *speclist )
    speclist = sort_list_by_shen_key( speclist )
    print( "Done." )

    print( "Writing multiplot... ", end="" )
    four_by_four_multiplot( pspec, *speclist, path=outpath, filename="Multi.pdf", plotTitle=f"{pns}: 1 sigma" )
    print( "Done." )

    print( "Writing results...", end="" )
    shen_dict = { }
    for k in r:
        shen_dict[ k ] = shenCat[ k ]
    namestring_dict_writer( shen_dict, outpath, f"{pns}.csv" )
    print( "Done." )
    return { pns: len( r ) }


def test( ):
    pass

if __name__ == '__main__':
    from multiprocessing import freeze_support

    freeze_support( )

    shenCat.load( )
    names = shenCat.keys( )
    n = len( names )
    final = { }
    running_count = join( BASE_PLOT_PATH, 'Ave Error Search', "running_count.csv" )
    for i in range( n ):
        pns = names.pop( i )
        print( f"--------------------    { pns }: {i + 1} / {n}" )
        final.update( single( pns, names ) )
        names.insert( i, pns )
        with open( running_count, 'a' ) as outfile:
            outfile.write( f"{pns},{final[pns]}{linesep}" )

    namestring_dict_writer( final, join( BASE_PLOT_PATH, 'Ave Error Search' ), "results-count.csv" )
    print( "Complete." )
