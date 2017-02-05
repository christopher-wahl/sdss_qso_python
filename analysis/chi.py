from spectrum import Spectrum

def chi( expSpec, obsSpec ):
    """
    Returns the chi^2 value between the given spectra

    :param expSpec: Expected Spectrum
    :param obsSpec: Observed Spectrum
     :type expSpec: Spectrum
     :type obsSpec: Spectrum
    :return: chi^2
    :rtype: float
    """
    a0 = expSpec.cpy( )
    a1 = obsSpec.cpy( )

    a0.alignToSpec( a1 )

    return sum( [ pow( a0.getFlux( wl ) - a1.getFlux( wl ), 2 ) / a0.getFlux( wl ) for wl in a0 ] )

def generic_chi( list0, list1 ):
    if len( list0 ) != len( list1 ):
        raise AssertionError( f"generic_chi: Lists are not of equal dimension\nLength list0: { len( list0 ) }\nLength list1: { len( list1 ) }")
    _chi = 0
    for i in range( len( list0 ) ):
        _chi += pow( list0[ i ] - list1[ i ], 2 ) / list0[ 0 ]
    return _chi

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