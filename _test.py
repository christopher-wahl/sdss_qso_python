# Looking through the division catalog to find divided spectra which have average values ~ 1
# when divided by "53521-1714-011"
#
# i.e. looking for spectra which are about as bright (in flux space) as "53521-1714-011"
#
# Note: the results in divCat are UNSCALED - thus the data looking through here is UNSCALED
#
from common import freeze_support
from common.constants import BASE_PLOT_PATH, BINNED_SPEC_PATH, join
from fileio.spec_load_write import async_load, bspecLoader


def main( ):
    from catalog import divCat, shenCat
    from analysis.pipeline import results_pipeline
    from tools.plot import ab_z_plot, make_line_plotitem, make_points_plotitem, four_by_four_multiplot
    from tools.cosmo import magnitude_evolution

    namestring = "53521-1714-011"
    divCat = divCat[ namestring ]
    r_dict = { }
    for k, v in divCat.items( ):
        r_dict[ k ] = v[ 2 ]  # DivCat Format: slope, intercept, ave

    div_pipe = results_pipeline( results_range=(0.9, 1.1), results=r_dict )
    results = div_pipe.reduce_results( )
    for k, v in results.items( ):
        print( f"{k}: {v}" )
    print( len( results ) )

    # Make the plot data
    z_data, ab_data, err_data = div_pipe.ab_v_z_data( True )
    p_z, p_ab, p_aberr = shenCat.subkey( namestring, 'z', 'ab', 'ab_err' )

    p_low_z = [ ]
    p_low_ab = [ ]

    p_high_z = [ ]
    p_high_ab = [ ]

    p_c_ab, p_c_z = [ ], [ ]

    # Making x,y data for the upper, lower, and central magnitude evolution
    for z, mag, ld in magnitude_evolution( p_ab - p_aberr, p_z ):
        p_low_z.append( z )
        p_low_ab.append( mag )

    for z, mag, ld in magnitude_evolution( p_ab + p_aberr, p_z ):
        p_high_z.append( z )
        p_high_ab.append( mag )

    for z, mag, ld in magnitude_evolution( p_ab, p_z ):
        p_c_z.append( z )
        p_c_ab.append( mag )

    points_data = make_points_plotitem( z_data, ab_data, error_data=err_data, color="royalblue" )
    p_low_data = make_line_plotitem( p_low_z, p_low_ab, title="Upper / Lower Expected Evolution", color="grey" )
    p_high_data = make_line_plotitem( p_high_z, p_high_ab, title="", color="grey" )
    p_c_data = make_line_plotitem( p_c_z, p_c_ab, title="", color="black" )

    ab_z_plot( p_low_data, p_high_data, p_c_data, points_data,
               plotTitle=f"Divided Average Values of 1 +/- 0.1 to {namestring}",
               path=join( BASE_PLOT_PATH, f"{namestring}-divsion" ), filename=f"{namestring}-divisons.pdf" )

    primary = bspecLoader( namestring )
    speclist = async_load( BINNED_SPEC_PATH, results.keys( ), 'bspec' )
    speclist.sort( key=lambda x: shenCat.subkey( x.getNS( ), 'z' ) )
    for spec in speclist:
        spec.setNS( f"{spec.getNS()} : z = {shenCat.subkey( spec.getNS(), 'z' )} : avg = {results[ spec.getNS() ] }" )

    four_by_four_multiplot( primary, *speclist, path=join( BASE_PLOT_PATH, f"{namestring}-divsion" ),
                            filename=f"{namestring}-div-multiplot.pdf",
                            plotTitle=f"Divisions to {namestring} wih average valeus of 1 +/ 0.1" )


if __name__ == "__main__":
    freeze_support( )
    main( )
