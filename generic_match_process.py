from typing import Union

from analysis.chi import em_chi_wrapper, pipeline_chi_wrapper
from analysis.pipeline import redshift_ab_pipeline, speclist_analysis_pipeline
from catalog import shenCat
from common import freeze_support
from common.constants import BASE_PLOT_PATH, SQUARE, STD_MAX_WL, STD_MIN_WL, join
from fileio.spec_load_write import async_bspec, bspecLoader
from spectrum import Spectrum, scale_enmasse
from tools.list_dict import sort_list_by_shen_key
from tools.plot import ab_z_plot, four_by_four_multiplot


def main( primary: Union[ Spectrum or str ] = None, n: float = 1 ) -> None:
    if primary is None:
        exit( "Primary is NoneType; cannot process without a spectrum" )
    elif isinstance( primary, str ):
        primary = bspecLoader( primary )

    # Get all the namestrings in shenCat
    # Then remove those which are not within n-sigma of the expected evolution
    catalog_names = shenCat.keys( )
    catalog_names.remove( primary.getNS( ) )

    print( f"Catalog loaded.  Reducing to all points within {n}-sigma of the expected evolution of {primary.getNS()}" )
    z_mag_pipe = redshift_ab_pipeline( primary_ns=primary.getNS( ), ns_of_interest=catalog_names )
    r = z_mag_pipe.reduce_results( )
    print( f"Done.  {len( r )} points remain." )

    """ First Pass """
    # Do EM line matching
    # Load the spec files
    print( f"Loading spectra in evolution range of {primary.getNS()} from disk" )
    speclist = scale_enmasse( primary, *async_bspec( sort_list_by_shen_key( r.keys( ) ) ) )
    print( "Done." )

    # No need to trim or scale, as the em_chi_wrapper does this via multiprocessing
    print( f"Beginning EM Line X{SQUARE} analysis" )
    em_chi_pipe = speclist_analysis_pipeline( primary, speclist, em_chi_wrapper, (0, 100) )
    em_chi_pipe.do_analysis( )
    r = em_chi_pipe.reduce_results( )
    print( f"Complete.  {len(r)} results remain." )

    """ Second - Continuum - Pass """
    # Reduce the speclist to those within em_chi results
    for i in range( len( speclist ) - 1, -1, -1 ):
        if speclist[ i ].getNS( ) not in r:
            del speclist[ i ]
    print( f"Beginning continuum analysis." )
    primary.trim( STD_MIN_WL, STD_MAX_WL )
    continuum_chi_pipe = speclist_analysis_pipeline( primary, speclist, pipeline_chi_wrapper, (0, 400) )
    continuum_chi_pipe.do_analysis( )
    r = continuum_chi_pipe.reduce_results( )
    print( f"Done. {len( r )} results remain." )

    print( "Plotting AB v Z and scaled spectra" )
    OUTPATH = join( BASE_PLOT_PATH, primary.getNS( ), "Generic" )
    primary = bspecLoader( primary.getNS( ) )
    speclist = scale_enmasse( primary, *sort_list_by_shen_key( async_bspec( list( r.keys( ) ) ) ) )
    ab_z_plot( primary, speclist, OUTPATH, "AB_Z Generic.pdf", plotTitle=f"Generic process {primary.getNS()}" )
    for spec in speclist:
        spec.setNS( f"{spec.getNS()} : z = {shenCat.subkey( spec.getNS(), 'z' )} : chi = {r[spec.getNS()]}" )
    four_by_four_multiplot( primary, *speclist, path=OUTPATH, filename="Multispec Generic.pdf" )
    print( "Plots complete." )



if __name__ == '__main__':
    freeze_support( )
    main( "53770-2376-290" )
