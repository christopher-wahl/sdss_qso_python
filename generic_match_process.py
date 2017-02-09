from typing import Union

from analysis.chi import em_chi_wrapper
from analysis.pipeline import redshift_ab_pipeline, speclist_analysis_pipeline
from catalog import shenCat
from common import freeze_support
from fileio.spec_load_write import async_bspec, bspecLoader
from spectrum import Spectrum
from tools import sort_list_by_shen_key


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
    speclist = async_bspec( sort_list_by_shen_key( r.keys( ) ) )

    # No need to trim or scale, as the em_chi_wrapper does this via multiprocessing
    chi_pipe = speclist_analysis_pipeline( primary, speclist, em_chi_wrapper, (0, 100) )
    chi_pipe.do_analysis( )
    r = chi_pipe.reduce_results( )

    # TODO: Finish Generic Process
    """ Second - Continuum - Pass """


if __name__ == '__main__':
    freeze_support( )
