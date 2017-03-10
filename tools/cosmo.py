from math import log10
from typing import List, Tuple, Union

from astropy import units
from astropy.cosmology import FlatLambdaCDM

# TODO: Form dl_string method to reduce call-recall of the same string.  Or just localize it into dl_from_Z

cosmo = FlatLambdaCDM( H0=67.74, Om0 = 0.3089 )

def dl_from_z( z ):
    """
    Calculates the luminosity distance at redshift z using the FlatLambdaCDM model with constraints of H0 = 67.74, Om0 = 0.3089
    (values from Wikipedia, 2016-07-21)

    :param z: Redshift at which to calculate luminosity distance
    :type z: float
    :return: Luminosity distance at z
    :rtype: float
    """
    return cosmo.luminosity_distance( z ).to( units.parsec ).value


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

    M_init = m0 - 5 * (log10( dl_from_z( z0 ) ) - 1)

    evolist = list()
    for z in arange( zlow, zhigh + step, step ):
        dL = dl_from_z( z )
        m = M_init + 5 * (log10( dL ) - 1)

        evolist.append( ( z, m, dL ) )
    if splitLists:
        return tuple( zip( *evolist ) )
    return evolist

def absolute_magnitude( m0, z0 ):
    """
    Returns absolute magnitude of a spectrum given apparent magnitude m0 at redshift z0

    Parameters
    ----------
    m0: float
    z0: float

    Returns
    -------
    M: float

    """
    return m0 - 5 * (log10( dl_from_z( z0 ) ) - 1)

def magnitude_at_redshift( m0, z0, z ):
    """
    Returns apparent magnitude at redshift z given apparent magnitude m0 at inital redshift z0

    Parameters
    ----------
    m0: float
    z0: float
    z: float

    Returns
    -------
    m: float

    """
    return absolute_magnitude( m0, z0 ) + 5 * (log10( dl_from_z( z ) ) - 1)

def difference_from_evolution( m0, z0, m1, z1 ):
    """
    Takes in the apparent magnitude and redshift of a primary spectrum ( m0, z0 ) and the apparent magnitude and redshift of a
    seconday spectrum ( m1, z1 ).  Calculates and returns the difference in apparent magnitude of the secondary to the prime spectrum
    by way of the magnitude evolution of the primary spectrum at the redshift of the secondary.

    Parameters
    ----------
    m0: float
        Apparent magnitude of the primary spectrum
    z0: float
        Redshift of the primary spectrum
    m1: float
        Apparent magnitude of the secondary spectrum
    z1: float
        Redshift of the secondary spectrum

    Returns
    -------
    difference: float
    """
    return m1 - magnitude_at_redshift( m0, z0, z1 )