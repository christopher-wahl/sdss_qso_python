# Looking through the division catalog to find divided spectra which have average values ~ 1
# when divided by "53521-1714-011"
#
# i.e. looking for spectra which are about as bright (in flux space) as "53521-1714-011"
#
# Note: the results in divCat are UNSCALED - thus the data looking through here is UNSCALED
#
from common import freeze_support
from common.constants import BASE_PLOT_PATH, join


def main( ):
    from catalog import shenCat
    from analysis.pipeline import redshift_ab_pipeline, speclist_analysis_pipeline
    from analysis.chi import em_chi_wrapper
    from fileio.spec_load_write import bspecLoader, async_bspec
    from tools.plot import ab_z_plot, four_by_four_multiplot
    from spectrum import scale_enmasse

    namestring = "53770-2376-290"
    prime = bspecLoader( namestring )
    names = shenCat.keys( )
    names.remove( namestring )

    rmp = redshift_ab_pipeline( namestring, ns_of_interest=names )
    rmp.reduce_results( 2 )
    rmp.plot_results( join( BASE_PLOT_PATH, namestring ), "AB_Z Sigma 2.pdf" )

    speclist = sorted( scale_enmasse( prime, *async_bspec( rmp.get_namestring_list( ) ) ),
                       key=lambda x: shenCat.subkey( x.getNS( ), 'z' ) )

    chi_pipe = speclist_analysis_pipeline( prime, speclist, em_chi_wrapper, (0, 100) )
    chi_pipe.do_analysis( )
    r = chi_pipe.reduce_results( )
    dupelist = [ ]
    for spec in speclist:
        if spec.getNS( ) in r:
            dupelist.append( spec )
    for spec in dupelist:
        spec.setNS( f"{spec.getNS()} : z = {shenCat.subkey( spec.getNS(), 'z' )} : chi^2 = {r[spec.getNS()]}" )
    speclist = [ ]
    ab_z_plot( namestring, chi_pipe, join( BASE_PLOT_PATH, namestring ), "AB_Z Reduced Chi 100.pdf",
               f"2 Sigma Evolution with EM Line X^2 < 100 for {namestring}" )
    four_by_four_multiplot( prime, *dupelist, path=join( BASE_PLOT_PATH, namestring ),
                            filename=f"{namestring} Chi 100 EM Line.pdf", plotTitle=f"{namestring} Chi 100 EM Line" )

    chi_pipe.set_range_limits( range_high=50 )
    r = chi_pipe.reduce_results( )
    speclist = sorted( scale_enmasse( prime, *async_bspec( list( r.keys( ) ) ) ),
                       key=lambda x: shenCat.subkey( x.getNS( ), 'z' ) )
    dupelist = speclist.copy( )
    for spec in dupelist:
        spec.setNS( f"{spec.getNS()} : z = {shenCat.subkey( spec.getNS(), 'z' )} : chi^2 = {r[spec.getNS()]}" )

    ab_z_plot( namestring, chi_pipe, join( BASE_PLOT_PATH, namestring ), "AB_Z Reduced Chi 50.pdf",
               f"2 Sigma Evolution with EM Line X^2 < 50 for {namestring}" )
    four_by_four_multiplot( prime, *dupelist, path=join( BASE_PLOT_PATH, namestring ),
                            filename=f"{namestring} Chi 50 EM Line.pdf", plotTitle=f"{namestring} Chi 50 EM Line" )


if __name__ == "__main__":
    freeze_support( )
    main( )
