from typing import Dict, Tuple

from spectrum import Spectrum


def chi( expSpec: Spectrum, obsSpec: Spectrum, doScale: bool = False, skipCopy: bool = False,
         wl_low_limit: float = None, wl_high_limit: float = None ) -> float:
    """
    Returns the chi^2 value between the given spectra

    :param expSpec: Expected Spectrum
    :param obsSpec: Observed Spectrum
    :param doScale: Scale the two spectra around DEF_SCALE_WL range
    :param wl_low_limit: Trim spectra to low limit before matching
    :param wl_high_limit: Trim spectra to high limit before matching
    :type expSpec: Spectrum
    :type obsSpec: Spectrum
    :type doScale: bool
    :type wl_low_limit: float
    :type wl_high_limit: float
    :return: chi^2
    :rtype: float
    """
    if not skipCopy:
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

    return sum( [ pow( a0.getFlux( wl ) - a1.getFlux( wl ), 2 ) / a0.getFlux( wl ) for wl in a0 ] )


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

def multi_chi_analysis( expSpec, speclist, MAX_PROC = None ):
    """
    Multiprocessing module for chi^2 analysis.  Returns a dictionary keyed by namestrings in the speclist with values of chi^2 result

    :param expSpec: Expected Spectrum
    :param speclist: list of Spectrum to perform analysis with expSpec
    :return: Dictionary of { namestring : chi^2 value }, namestrings taken from the respective speclist entrys
    :rtype: dict
    """
    from common.async_tools import generic_unordered_multiprocesser as multiproc

    results = []
    multiproc( [ ( expSpec, spec ) for spec in speclist ], __multi_chi_wrapper, results, MAX_PROC )

    resultsDict = {}
    for result in results:
        resultsDict.update( result )

    return resultsDict

def __multi_chi_wrapper( inputV ):
    """
    Wrapper for multi_chi_analysis, passed into multiprocessing module

    :param inputV: tuple item from input_values list; unpacked in module to ( expSpec, obsSpec ) to pass into chi()
    :type inputV: tuple
    :return: Dictionary of { obsSpec.namestring : chi^2 result }
    :rtype: dict
    """
    expSpec, obsSpec = inputV
    return { obsSpec.getNS() : chi( expSpec, obsSpec ) }

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
