from analysis.pipeline import speclist_analysis_pipeline
from catalog import shenCat
from common.constants import BASE_PLOT_PATH, HB_RANGE, HG_RANGE, MGII_RANGE, OIII_RANGE, linesep
from fileio.spec_load_write import async_bspec, bspecLoader
from spectrum import List, Spectrum, scale_enmasse
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


def main( ):
    shenCat.load( )
    pns = "53770-2376-290"
    names = shenCat.keys( )
    names.remove( pns )

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
    print( "Reducing results...." )
    r = chi_pipe.reduce_results( )
    cut_speclist( speclist, r )
    print( f"{len( r )} remain.", end=linesep )

    ab_z_plot( path=BASE_PLOT_PATH, filename="MGII.pdf", primary=pns, points=r )

    err = pspec.aveErr( wl_range=HB_RANGE ) / 2
    print( f"Building the HB anaylsis pipeline with maximum value {err}...", end="" )
    input_values = [ (pspec, spec, HB_RANGE) for spec in speclist ]
    chi_pipe = speclist_analysis_pipeline( pspec, speclist, reduced_chi_wrapper,
                                           (0, err), input_values )
    print( "Done", end=linesep )

    print( "Running HB pipeline.... ", end="" )
    chi_pipe.do_analysis( )
    print( "Reducing results...." )
    r = chi_pipe.reduce_results( )
    cut_speclist( speclist, r )
    print( len( speclist ) )
    print( f"{len( r )} remain.", end=linesep )

    ab_z_plot( path=BASE_PLOT_PATH, filename="MGII and HB.pdf", primary=pns, points=r )

    err = pspec.aveErr( wl_range=OIII_RANGE ) / 2
    print( f"Building the OIII anaylsis pipeline with maximum value {err}...", end="" )
    input_values = [ (pspec, spec, OIII_RANGE) for spec in speclist ]
    chi_pipe = speclist_analysis_pipeline( pspec, speclist, reduced_chi_wrapper,
                                           (0, err), input_values )
    print( "Done", end=linesep )

    print( "Running OIII pipeline.... ", end="" )
    chi_pipe.do_analysis( )
    print( "Reducing results...." )
    r = chi_pipe.reduce_results( )
    cut_speclist( speclist, r )
    print( f"{len( r )} remain.", end=linesep )

    ab_z_plot( path=BASE_PLOT_PATH, filename="MGII, HB and OIII.pdf", primary=pns, points=r )

    err = pspec.aveErr( wl_range=HG_RANGE ) / 2
    print( f"Building the HG anaylsis pipeline with maximum value {err}...", end="" )
    input_values = [ (pspec, spec, HG_RANGE) for spec in speclist ]
    chi_pipe = speclist_analysis_pipeline( pspec, speclist, reduced_chi_wrapper,
                                           (0, err), input_values )
    print( "Done", end=linesep )

    print( "Running HG pipeline.... ", end="" )
    chi_pipe.do_analysis( )
    print( "Reducing results...." )
    r = chi_pipe.reduce_results( )
    cut_speclist( speclist, r )
    print( f"{len( r )} remain.", end=linesep )

    print( "Scaling speclist...", end="" )
    speclist = scale_enmasse( pspec, *speclist )
    print( "Done." )
    ab_z_plot( path=BASE_PLOT_PATH, filename="MGII, HB and OIII and HG.pdf", primary=pns, points=r )
    print( "Writing multiplot... ", end="" )
    four_by_four_multiplot( pspec, *speclist, path=BASE_PLOT_PATH, filename="Multi.pdf" )
    print( "Done." )


def test( ):
    pass

if __name__ == '__main__':
    from multiprocessing import freeze_support

    freeze_support( )
    main( )
