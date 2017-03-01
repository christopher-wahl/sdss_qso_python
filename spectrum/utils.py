from typing import List, Union

from spectrum import Spectrum


def compose_speclist( speclist: List[ Spectrum ], namestring: str = "" ) -> Spectrum:
    """
    Forms a composite spectrum from the given input spectra

    :param speclist: List of Spectrum to compose
    :param namestring: Namestring to assign to the composite
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
                joined[ wl ] = list( )
            joined[ wl ].append( spec.get( wl ) )

    wavelength_list = [ ]
    fluxlist = [ ]
    errlist = [ ]

    for wl, v in joined.items( ):
        wavelength_list.append( wl )
        if len( v ) > 1:
            fluxlist.append( mean( [ f[ 0 ] for f in v ] ) )
            errlist.append( std( [ e[ 1 ] for e in v ] ) )
        else:
            fluxlist.append( v[ 0 ][ 0 ] )
            errlist.append( v[ 0 ][ 1 ] )

    composite.setDict( wavelength_list, fluxlist, errlist )

    return composite


def drop_to_em_lines( spec: Spectrum, *speclist: list, mgii=True, hb=True ) -> Union[ Spectrum, list ]:
    """
    Will drop all but standard EM line range for MgII and Hb (defined in common.constants) from given spectra.
    If more than one passed, will operate on all of them and return a list in the order in which they were passed.

    Pass mgii = False or hb = False to also drop the standard ranges included in these values.

    Directly modifies the spectra

    :param spec: spectrum to be operated on
    :param mgii: Defaults to True, will keep MgII line
    :param hb:  Defaults to True, will keep Hb line
    :type spec: Spectrum
    :type mgii: bool
    :type hb: bool
    :return: Spectrum or [ Spectrum ] depending on number passed in
    :rtype: Spectrum or list
    """
    speclist = list( speclist ) or [ ]
    speclist.insert( 0, spec )

    if len( speclist ) > 20:
        from common.async_tools import generic_ordered_multiprocesser
        input_values = [ (spec, mgii, hb) for spec in speclist ]
        output_values = [ ]
        generic_ordered_multiprocesser( input_values, __em_drop_wrapper, output_values )
        for i in range( len( output_values ) ):
            del speclist[ i ]
            speclist.insert( i, output_values[ i ] )
    else:
        for i in range( len( speclist ) ):
            speclist[ i ] = __em_drop_wrapper( (speclist[ i ], mgii, hb) )

    if len( speclist ) == 1:
        return speclist[ 0 ]
    return speclist


def __em_drop_wrapper( inputV ) -> Spectrum:
    from common.constants import MGII_RANGE, HB_RANGE
    spec, mgii, hb = inputV
    wls = spec.getWavelengths( )
    for wl in wls:

        if mgii and hb:
            if (MGII_RANGE[ 0 ] <= wl <= MGII_RANGE[ 1 ]) or (HB_RANGE[ 0 ] <= wl <= HB_RANGE[ 0 ]):
                continue
            del spec[ wl ]
        elif mgii and not (MGII_RANGE[ 0 ] <= wl <= MGII_RANGE[ 1 ]):
            del spec[ wl ]
        elif hb and not (HB_RANGE[ 0 ] <= wl <= HB_RANGE[ 1 ]):
            del spec[ wl ]
    return spec


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
        spec.scale( scalewl=scale_wl, scaleflx=scaleflx, radius=scale_radius )

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
