from typing import Dict, Tuple

from spectrum import List, Spectrum, Union


def chi( expSpec: Spectrum, obsSpec: Spectrum, doScale: bool = False, skipCopy: bool = False,
         wl_low_limit: float = None, wl_high_limit: float = None, n_sigma: float = 1,
         old_process: bool = False, get_count: bool = False, skip_2cpy = False ) -> float:
    """
    Returns the chi^2 value between the given spectra

    :param expSpec: Expected Spectrum
    :param obsSpec: Observed Spectrum
    :param doScale: Scale the two spectra around DEF_SCALE_WL range
    :param wl_low_limit: Trim spectra to low limit before matching
    :param wl_high_limit: Trim spectra to high limit before matching
    :param n_sigma: Multiplicative flux-err range to zero.  ie. Any value falling within flux +/- n_sigma * err = 0
    :type expSpec: Spectrum
    :type obsSpec: Spectrum
    :type doScale: bool
    :type wl_low_limit: float
    :type wl_high_limit: float
    :type n_sigma: float
    :return: chi^2
    :rtype: float
    """
    if skip_2cpy:
        a0 = expSpec.cpy( )
        a1 = obsSpec
    elif not skipCopy:
        a0 = expSpec.cpy( )
        a1 = obsSpec.cpy( )
    else:
        a0 = expSpec
        a1 = obsSpec

    if( doScale ):
        a1.scale( spec = a0 )

    if wl_low_limit is not None:
        a0.trim( wlLow=wl_low_limit )
        a1.trim( wlLow=wl_low_limit )

    if wl_high_limit is not None:
        a0.trim( wlHigh=wl_high_limit )
        a1.trim( wlHigh=wl_high_limit )

    a0.alignToSpec( a1 )

    # old system, uncontrolled for error.  Left in for testing.
    if old_process:
        s = sum( [ pow( a0.getFlux( wl ) - a1.getFlux( wl ), 2 ) / a0.getFlux( wl ) for wl in a0 ] )
    else:
        s = 0
        for wl in a0:
            a0_f, a0_e = a0[ wl ]
            low, high = a0_f + n_sigma * a0_e, a0_f - n_sigma * a0_e
            a1_f, a1_e = a1[ wl ]

            # determine if errors overlap
            if abs( a0_f - a1_f ) < n_sigma * (a0_e + a1_e):
                continue

            s += pow( a1_f - a0_f, 2 ) / a0_f
    if get_count:
        s = (s, len( a0 ))
    return s


def generic_chi( list0: list, list1: list ) -> float:
    """
    Returns the Chi^2 value between two lists of equal lengths

    :param list0: Expected
    :param list1: Observed
    :return: chi^2
    :rtype: float
    :raises: AssertionError
    """
    if len( list0 ) != len( list1 ):
        raise AssertionError( f"generic_chi: Lists are not of equal dimension\nLength list0: { len( list0 ) }\nLength list1: { len( list1 ) }")
    _chi = 0
    for i in range( len( list0 ) ):
        _chi += pow( list0[ i ] - list1[ i ], 2 ) / list0[ 0 ]
    return _chi

@DeprecationWarning
def async_chi_analysis( expSpec, speclist ):
    async def __async_chi_wrapper( expSpec, obsSpec ):
        return { obsSpec.getNS() : chi( expSpec, obsSpec ) }

    from common.async_tools import generic_async_wrapper
    import asyncio

    results = []
    chi_loop = asyncio.new_event_loop()
    try:
        chi_loop.run_until_complete( generic_async_wrapper( [ ( expSpec, spec ) for spec in speclist ], __async_chi_wrapper, results ) )
    finally:
        chi_loop.close()

    resultsDict = {}
    for result in results:
        resultsDict.update( result )

    return resultsDict


def multi_chi_analysis( expSpec: Spectrum, speclist: List[ Spectrum ], getlist: bool = False, **kwargs ) -> Union[
    List[ Tuple[ str, float ] ], dict ]:
    """
    Multiprocessing module for chi^2 analysis.  Returns a dictionary keyed by namestrings in the speclist with values of chi^2 result

    :param expSpec: Expected Spectrum
    :param speclist: list of Spectrum to perform analysis with expSpec
    :return: Dictionary of { namestring : chi^2 value }, namestrings taken from the respective speclist entrys
    :rtype: dict
    """
    from common.async_tools import generic_unordered_multiprocesser

    results = []
    input_values = [ (expSpec, spec, kwargs) for spec in speclist ]
    generic_unordered_multiprocesser( input_values, __multi_chi_wrapper, results )
    if getlist:
        return results
    return dict( results )

def __multi_chi_wrapper( inputV ):
    """
    Wrapper for multi_chi_analysis, passed into multiprocessing module

    :param inputV: tuple item from input_values list; unpacked in module to ( expSpec, obsSpec ) to pass into chi()
    :type inputV: tuple
    :return: Dictionary of { obsSpec.namestring : chi^2 result }
    :rtype: dict
    """
    expSpec, obsSpec = inputV[ :2 ]
    kwargs = { }
    [ kwargs.update( pt ) for pt in inputV[ 2: ] ]
    return (obsSpec.getNS( ), chi( expSpec, obsSpec, **kwargs ))

def pipeline_chi_wrapper( inputV ):
    return __multi_chi_wrapper( inputV )

def em_chi_wrapper( inputV: Tuple[ Spectrum, Spectrum ] ) -> Dict[ str, float ]:
    """
    Wrapper for running chi^2 over EM lines alone.  Scales obsSpec to expSepc before trimming to EM lines

    :param inputV: Tuple of ( expected_spectrum, observed_spectrum )
    :type inputV: Tuple( Spectrum, Spectrum )
    :return: Dictionary of { observed_spectrum.getNS() : chi( expected_spectrum, observed_spectrum )
    :rtype: Dict[ str : float ]
    """
    from spectrum import drop_to_em_lines
    expSpec, obsSpec = inputV
    try:
        obsSpec.scale( spec=expSpec )
    except ZeroDivisionError:
        print( "em_chi_wrapper: Unable to scale spectra - Is the default aveFlux range still in the spectrum?" )
        print( expSpec, '\n', obsSpec )
    expSpec, obsSpec = drop_to_em_lines( expSpec.cpy( ), obsSpec.cpy( ) )
    return { obsSpec.getNS( ): chi( expSpec, obsSpec, doScale=False, skipCopy=True ) }


def fwhm( spec: Spectrum, wl_range: Tuple[ float, float ] ) -> float:
    spec = spec.cpy( )
    spec.trim( wl_range=wl_range )

    wls = spec.getWavelengths( )

    max_wl = min_wl = wls[ 0 ]
    min_flux = spec.getFlux( min_wl )
    max_flux = spec.getFlux( max_wl )
    for wl in wls:
        if min_flux > spec.getFlux( wl ):
            min_flux = spec.getFlux( wl )
            min_wl = wl
        elif max_flux < spec.getFlux( wl ):
            max_flux = spec.getFlux( wl )
            max_wl = wl

    half_max_position = spec.nearest( (min_wl - max_wl) / 2 )

    return 2 * (max_wl - half_max_position)
