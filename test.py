from analysis.chi import pipeline_chi_wrapper
from analysis.pipeline import redshift_ab_pipeline, speclist_analysis_pipeline
from catalog import divCat, shenCat
from common.constants import BASE_PLOT_PATH, BINNED_SPEC_PATH, STD_MAX_WL, STD_MIN_WL, freeze_support
from fileio.spec_load_write import async_load, bspecLoader


def main():
    shenCat.load()

    ns = "53521-1714-011"
    z, ab, aberr = shenCat.subkey( ns, 'z', 'ab', 'ab_err' )
    divCat.load( namestring=ns )

    from catalog import chiCat
    chiCat.load()

    print( len( chiCat[ ns ].keys() ) )
    exit()

    rmp = redshift_ab_pipeline( ns, z, ab, aberr, divCat[ ns ] )
    rmp.reduce_results()
    outd = rmp.bin_results()
    rmp.plot_results( BASE_PLOT_PATH, f"{ns} Catalog Entries in Range.pdf")

    bspecnames = list( rmp.get_results().keys() )
    speclist = async_load( BINNED_SPEC_PATH, bspecnames, ".bspec")
    prime = bspecLoader( ns )

    chi_analysis = speclist_analysis_pipeline( prime, speclist, pipeline_chi_wrapper, ( 0, 1000 ) )
    chi_analysis.trim_prime( STD_MIN_WL, STD_MAX_WL )
    chi_analysis.do_analysis()
    chi_analysis.reduce_results()
    r = chi_analysis.get_results()
    rmp.set_results( r )
    rmp.plot_results( BASE_PLOT_PATH, f"{ns} Chi max 1000.pdf" )

    chi_analysis = speclist_analysis_pipeline( prime, speclist, pipeline_chi_wrapper, ( 0, 500 ) )
    chi_analysis.trim_prime( STD_MIN_WL, STD_MAX_WL )
    chi_analysis.do_analysis()
    chi_analysis.reduce_results( )
    r = chi_analysis.get_results()
    rmp.set_results( r )
    rmp.plot_results( BASE_PLOT_PATH, f"{ns} Chi max 500.pdf" )

    print( "test")

if __name__ == "__main__":
    freeze_support()
    main()