#
# Doing usual EM line search, then doing OIII line search
#
#


from typing import List, Union

from analysis.chi import pipeline_chi_wrapper
from analysis.pipeline import redshift_ab_pipeline, speclist_analysis_pipeline
from catalog import shenCat
from common import freeze_support
from common.constants import BASE_PLOT_PATH, HB_RANGE, HG_RANGE, MGII_RANGE, OIII_RANGE, SQUARE, join
from fileio.spec_load_write import async_bspec, bspecLoader
from spectrum import Spectrum, scale_enmasse
from tools.list_dict import sort_list_by_shen_key
from tools.plot import ab_z_plot, four_by_four_multiplot

EM_MAX = 0.3


def get_and_scale_speclsit( primary: Spectrum, names_list: list ) -> List[ Spectrum ]:
    # Do EM line matching
    # Load the spec files
    print( f"Loading spectra in evolution range of {primary.getNS()} from disk" )
    names_list = sort_list_by_shen_key( names_list )
    speclist = async_bspec( names_list )
    # speclist = scale_enmasse( primary, *speclist )
    print( "Done." )
    return speclist


def do_z_pipe( primary: Spectrum, catalog_names: list, n: float ) -> dict:
    print( f"Catalog loaded.  Reducing to all points within {n}-sigma of the expected evolution of {primary.getNS()}" )
    z_mag_pipe = redshift_ab_pipeline( primary_ns=primary.getNS( ), ns_of_interest=catalog_names )
    r = z_mag_pipe.reduce_results( )
    print( f"Done.  {len( r )} points remain." )
    return r

def dim_primary( primary: Spectrum, target: Spectrum ) -> Spectrum:
    primary = primary.cpy( )
    primary.dim_to_ab( target.magAB( ) )
    return primary


def dim_chi_wrapper( inputV ):
    p, t = inputV
    p = dim_primary( p, t )
    return pipeline_chi_wrapper( (p, t) )


def o3_wrapper( inputV ):
    p, t = inputV
    p = dim_primary( p, t )
    p.trim( wl_range=OIII_RANGE )
    return pipeline_chi_wrapper( (p, t) )


def mg_wrapper( inputV ):
    p, t = inputV
    p = dim_primary( p, t )
    p.trim( wl_range=MGII_RANGE )
    return pipeline_chi_wrapper( (p, t) )


def hb_wrapper( inputV ):
    p, t = inputV
    p = dim_primary( p, t )
    p.trim( wl_range=HB_RANGE )
    return pipeline_chi_wrapper( (p, t) )


def hg_wrapper( inputV ):
    p, t = inputV
    p = dim_primary( p, t )
    p.trim( wl_range=HG_RANGE )
    return pipeline_chi_wrapper( (p, t) )

def o3_pass( primary: Spectrum, speclist: List[ Spectrum ] ) -> dict:
    print( f"Beginning OIII analysis." )
    o3_chi = speclist_analysis_pipeline( primary, speclist, o3_wrapper, (0, EM_MAX) )
    o3_chi.do_analysis( )
    r = o3_chi.reduce_results( )
    print( f"Complete.  {len(r)} results remain." )
    return r


def mg_pass( primary: Spectrum, speclist: List[ Spectrum ] ) -> dict:
    print( f"Beginning MGII X{SQUARE} analysis" )
    # No need to trim or scale, as the em_chi_wrapper does this via multiprocessing
    em_chi_pipe = speclist_analysis_pipeline( primary, speclist, mg_wrapper, (0, EM_MAX) )
    em_chi_pipe.do_analysis( )
    r = em_chi_pipe.reduce_results( )
    print( f"Complete.  {len(r)} results remain." )
    return r


def hb_pass( primary: Spectrum, speclist: List[ Spectrum ] ) -> dict:
    print( f"Beginning HB X{SQUARE} analysis" )
    # No need to trim or scale, as the em_chi_wrapper does this via multiprocessing

    em_chi_pipe = speclist_analysis_pipeline( primary, speclist, hb_wrapper, (0, EM_MAX) )
    em_chi_pipe.do_analysis( )
    r = em_chi_pipe.reduce_results( )
    print( f"Complete.  {len(r)} results remain." )
    return r


def hg_pass( primary: Spectrum, speclist: List[ Spectrum ] ) -> dict:
    print( f"Beginning HG X{SQUARE} analysis" )
    # No need to trim or scale, as the em_chi_wrapper does this via multiprocessing

    em_chi_pipe = speclist_analysis_pipeline( primary, speclist, hg_wrapper, (0, EM_MAX) )
    em_chi_pipe.do_analysis( )
    r = em_chi_pipe.reduce_results( )
    print( f"Complete.  {len(r)} results remain." )
    return r

def main( primary: Union[ Spectrum or str ] = None, n: float = 1 ) -> None:
    if primary is None:
        exit( "Primary is NoneType; cannot process without a spectrum" )
    elif isinstance( primary, str ):
        primary = bspecLoader( primary )

    # Get all the namestrings in shenCat
    # Then remove those which are not within n-sigma of the expected evolution
    catalog_names = shenCat.keys( )
    catalog_names.remove( primary.getNS( ) )

    r = shenCat
    r = do_z_pipe( primary, catalog_names, n )

    """ First Pass - MGII and HB """
    speclist = get_and_scale_speclsit( primary, list( r.keys( ) ) )
    r = mg_pass( primary, speclist )
    primary = bspecLoader( primary.getNS( ) )
    speclist = sort_list_by_shen_key( async_bspec( list( r.keys( ) ) ) )
    r = hb_pass( primary, speclist )
    primary = bspecLoader( primary.getNS( ) )
    speclist = sort_list_by_shen_key( async_bspec( list( r.keys( ) ) ) )
    r = hg_pass( primary, speclist )

    """ Second - OIII - Pass
    This process is manual, since I haven't written anything to deal with OIII lines
    """
    # Reduce the speclist to those within em_chi results
    primary = bspecLoader( primary.getNS( ) )
    speclist = sort_list_by_shen_key( async_bspec( list( r.keys( ) ) ) )
    r = o3_pass( primary, speclist )
    del speclist
    primary = bspecLoader( primary.getNS( ) )
    speclist = sort_list_by_shen_key( async_bspec( list( r.keys( ) ) ) )

    """ Third Pass - Continuum """
    """print( f"Beginning continuum analysis." )
    primary.trim( STD_MIN_WL, STD_MAX_WL )
    continuum_chi_pipe = speclist_analysis_pipeline( primary, speclist, dim_chi_wrapper, (0, 300) )
    continuum_chi_pipe.do_analysis( )
    r = continuum_chi_pipe.reduce_results( )
    print( f"Done. {len( r )} results remain." )"""

    print( "Plotting AB v Z and scaled spectra" )
    OUTPATH = join( BASE_PLOT_PATH, primary.getNS( ), "Generic", "Dim Process" )
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
