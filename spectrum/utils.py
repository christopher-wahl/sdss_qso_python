from typing import Iterable, List, Tuple, Union

from common.constants import DEFAULT_SCALE_RADIUS, DEFAULT_SCALE_WL
from spectrum import Spectrum


def align_wavelengths( s0: Iterable, s1: Iterable, wl_low: float = None, wl_high: float = None ) -> set:
    """
    Takes in an iterable (such as a Spectrum or list of wavelengths), and returns the set of wavelengths for which the
    two interset.  Should wl_low or wl_high be passed, the set will be limited to wl_low <= values <= wl_high, as
    applicable.

    While this is intended to align wavelength values, it will technically work with any type of object for which
    comparison operators ( -, <=, >= ) can be conducted.

    :param s0: first Iterable of values 
    :param s1: second Iterable of values 
    :param wl_low: Minimum wavelength values.  Defaults to None.
    :param wl_high: Maximum wavelength values  Defaults to None.
    :return: Set of values contained in both iterables, limited to wl_low / wl_high as applicable
    :rtype: set
    """
    wls = set( s0 ).intersection( s1 )
    if wl_low is not None:
        wls = filter( lambda x: x >= wl_low, wls )
    if wl_high is not None:
        wls = filter( lambda x: x <= wl_high, wls )
    return set( wls )


def compose_speclist( speclist: List[ Spectrum ], namestring: str = "" ) -> Spectrum:
    """
    Forms a composite spectrum from the given input spectra

    :param speclist: List of Spectrum to compose
    :param namestring: Namestring to assign to the composite.  Defaults to ""
    :type speclist: list
    :type namestring: str
    :return: Composite Spectrum
    :rtype: Spectrum
    """
    from numpy import std, mean

    joined = { }
    composite = Spectrum( ns=namestring )
    for spec in speclist:
        for wl in spec:
            if wl not in joined:
                joined[ wl ] = list()
            joined[ wl ].append( spec.get( wl ) )

    wavelength_list = [ ]
    fluxlist = [ ]
    errlist = [ ]

    for wl, v in joined.items():
        wavelength_list.append( wl )
        if len( v ) > 1:
            fluxlist.append( mean( [ f[ 0 ] for f in v ] ) )
            errlist.append( std( [ e[ 1 ] for e in v ] ) )
        else:
            fluxlist.append( v[ 0 ][ 0 ] )
            errlist.append( v[ 0 ][ 1 ] )

    composite.setDict( wavelength_list, fluxlist, errlist )

    return composite


def scale_enmasse( primary_spectrum: Spectrum, speclist: List[ Spectrum ], scale_wl: float = None,
                   scale_radius: float = None ) -> Union[ List[ Spectrum ] or Spectrum ]:
    """
    Directly modifies the spectrum arguments when are passed as *speclist to scale them to primary_spectrum

    Nonkwargs passed after primary_spectrum will be handled as *args; i.e. passed as members of speclist

    :param primary_spectrum: Primary spectrum to scale to
    :param speclist: List of spectrum to scale
    :param scale_wl: Central scaling wavelength; defaults to common.constants.DEFAULT_SCALE_WL
    :param scale_radius: Radius to use for average flux determination; defaults to common.constants.DEFAULT_SCALE_RADIUS
    :type primary_spectrum: Spectrum
    :type speclist: list
    :type scale_wl: float
    :type scale_radius: float
    :return: speclist
    :rtype: List[ Spectrum ] or Spectrum
    """
    if scale_wl is None:
        from common.constants import DEFAULT_SCALE_WL
        scale_wl = DEFAULT_SCALE_WL
    if scale_radius is None:
        from common.constants import DEFAULT_SCALE_RADIUS
        scale_radius = DEFAULT_SCALE_RADIUS

    scaleflx = primary_spectrum.aveFlux( scale_wl, scale_radius )
    for spec in speclist:
        spec.scale( scaleWL=scale_wl, scaleflux=scaleflx, radius=scale_radius )

    if (len( speclist )) == 1:
        return speclist[ 0 ]
    return list( speclist )


def find_nearest_wavelength( sorted_wavelengths: List[ float ], wavelength: float ) -> float:
    """
    Finds the value of the nearest wavelength in the sorted list sorted_wavelengths.

    :param sorted_wavelengths: List of wavelengths to parse
    :param wavelength: Value of interest
    :type sorted_wavelengths: list
    :type wavelength: float
    :return: Nearest value to wavelength contained withiin sorted_wavelengths
    :rtype: float
    """
    from bisect import bisect_left

    pos = bisect_left( sorted_wavelengths, wavelength )
    if pos == 0:
        return sorted_wavelengths[ 0 ]
    if pos == len( sorted_wavelengths ):
        return sorted_wavelengths[ -1 ]
    before = sorted_wavelengths[ pos - 1 ]
    after = sorted_wavelengths[ pos ]
    if after - wavelength < wavelength - before:
        return after
    else:
        return before


def mutli_scale( primary: Spectrum, speclist: List[ Spectrum ], scale_wl: float = DEFAULT_SCALE_WL,
                 scale_radius=DEFAULT_SCALE_RADIUS ) -> List[ Spectrum ]:
    from tools.async_tools import generic_ordered_multiprocesser

    scale_flux = primary.aveFlux( central_wl=scale_wl, radius=scale_radius )

    inputV = [ (spec, scale_flux, scale_wl, scale_radius) for spec in speclist ]
    speclist = [ ]
    generic_ordered_multiprocesser( inputV, __multi_scale_wrapper, speclist )
    return speclist


def __multi_scale_wrapper( inputV: Tuple[ Spectrum, float, float, float ] ) -> Spectrum:
    spec, scale_flux, scale_wl, scale_radius = inputV
    spec.scale( scaleflux=scale_flux, scaleWL=scale_wl, radius=scale_radius )
    return spec


def reduce_speclist( namelist: Iterable[ str ], speclist: List[ Spectrum ] ) -> None:
    """
    Deletes any spectrum in speclist with a namestring not contained in namelist

    :param namelist: Iterable of namestrings
    :param speclist: List of Spectrum
    :type namelist: Iterable
    :type speclist: list
    :return: None
    """
    for i in range( len( speclist ) - 1, -1, -1 ):
        if speclist[ i ].getNS() not in namelist:
            del speclist[ i ]


def flux_from_AB( ABmag: float, wavelength: float = DEFAULT_SCALE_WL ) -> float:
    # Convert AB magntiude to flux_frequency
    exponent = (8.9 - ABmag) / 2.5
    f_v = pow( 10, exponent )

    # Conert flux_frequency to flux_wavelength, and put into SDSS units
    return f_v / (3.34E4 * 1E-17 * pow( wavelength, 2 ))
