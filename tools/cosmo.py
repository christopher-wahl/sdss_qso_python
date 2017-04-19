"""
This method creates a single instance of the FlatLambdaCDM in astropy and uses it to
evolve magnitudes with redshift (via the luminosity distance relation).

FlatLambdaCDM model with constraints of H0 = 67.6, Om0 = 0.3089 (values from SDSS BOSS, published 2016-07-13 and 
        1-Omega_Lambda = 1 - 0.6911 = 0.3089 from the Planck Collaboration in 2015)
"""
from math import log10
from typing import List, Tuple, Union

from astropy import units
from astropy.cosmology import FlatLambdaCDM

__cosmo = FlatLambdaCDM( H0=67.6, Om0=0.3089 )


def luminsoity_distance_from_redshift( z: float ) -> float:
    """
    Calculates the luminosity distance (in parsecs) at redshift z using the Flat Lambda CDM

    :param z: Redshift at which to calculate luminosity distance
    :type z: float
    :return: Luminosity distance at redshift z in terms of parsecs
    :rtype: float
    """
    return __cosmo.luminosity_distance( z ).to( units.parsec ).value


def magnitude_evolution( m0: float, z0: float, zrange: tuple = (0.46, 0.82), step: float = 0.01,
                         splitLists: bool = False ) -> Union[ List[
                                                                  Tuple[ float, float, float ] ], Tuple[
                                                                  tuple, tuple, tuple ] ]:
    """
    Generates the apparent magnitude evolution of a spectrum given its magnitude m0 at redshift z0.  Default zrange = ( 0.46, 0.82 ), step size of 0.01.

    Returns a list from lowest to highest redshift of tuples ( z, apparent magnitude at z, luminosity distance )

    If splitList is True, returns a single tuple of three lists ( ( z ), ( magnitude ), ( ld ) )

    :param m0: Initial apparent magnitude
    :param z0: Initial redshift at which apparent magnitude was observed
    :param zrange: Range of redshifts to calculate evolution over.  Defaults to ( 0.46, 0.82 ).
        Will run loop from low value to high value + step such that the high value is included
    :param step: step size to iterate over zrange.  Defaults to 0.01
    :param splitLists: If True, returns a single tuple of ( ( z_data ), ( magnitude_data ), ( luminosity_distance ) ) lists
    :type m0: float
    :type z0: float
    :type zrange: tuple
    :type step: float
    :type splitLists: bool
    :return: List of tuples [ ( redshift, apparent_magnitude at z, luminosity_distance), ... ] or Tuple of tuples ( ( z ), ( mag ), ( ld ) )
    :rtype: list or tuple
    """
    from numpy import arange
    zlow, zhigh = zrange

    M_init = m0 - 5 * (log10( luminsoity_distance_from_redshift( z0 ) ) - 1)

    evolist = list()
    for z in arange( zlow, zhigh + step, step ):
        dL = luminsoity_distance_from_redshift( z )
        m = M_init + 5 * (log10( dL ) - 1)

        evolist.append( (z, m, dL) )
    if splitLists:
        return tuple( zip( *evolist ) )
    return evolist


def absolute_magnitude( m0, z0 ):
    """
    Returns absolute magnitude of a spectrum given apparent magnitude m0 at redshift z0
    via the relation
    
    M_abs = m_app - 5 * log10( Luminosity Distance - 1 )
    
    :param m0: Apparent magnitude
    :param z0: Redshift
    :type m0: float
    :type z0: float
    :return: Absolute magnitude
    :rtype: float
    """
    return m0 - 5 * (log10( luminsoity_distance_from_redshift( z0 ) ) - 1)


def apparent_magnitude_at_redshift( m0, z0, z ):
    """
    Given a known apparent magnitude m0 and redshift z0, returns the apparent magnitude of an object if
    it were moved to redshift z using the Flat Lambda CDM.
    
    :param m0: Known apparent magnitude
    :param z0: Known redshift
    :param z: Redshift at which apparent magnitude is desired
    :type m0: float
    :type z0: float
    :type z: float
    :return: Apparent magnetude at redshift z
    :rtype: float
    """
    return absolute_magnitude( m0, z0 ) + 5 * (log10( luminsoity_distance_from_redshift( z ) ) - 1)
