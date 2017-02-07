from typing import Union

from .Spectrum import Spectrum

def drop_to_em_lines( spec : Spectrum, *speclist : list, mgii = True, hb = True) -> Union[ Spectrum, list ]:
    """
    Will drop all but standard EM line range for MgII and Hb (defined in common.constants) from given spectra.
    If more than one passed, will operate on all of them and return a list in the order in which they were passed.

    Pass mgii = False or hb = False to also drop the standard ranges included in these values.

    Directly modifies the spectra

    :param spec: spectrum to be operated on
    :param mgii: Defaults to True, will keep MgII line
    :param hb:  Defaults to True, will keep Hb line
    :param copy: Defaults to True, will make copy of each item before operating
    :type spec: Spectrum
    :type mgii: bool
    :type hb: bool
    :return: Spectrum or [ Spectrum ] depending on number passed in
    :rtype: Spectrum or list
    """
    speclist = list( speclist ) or []
    speclist.insert( 0, spec )

    if len( speclist ) > 20:
        from common.async_tools import generic_ordered_multiprocesser
        input_values = [ ( spec, mgii, hb ) for spec in speclist ]
        output_values = []
        generic_ordered_multiprocesser( input_values, __em_drop_wrapper, output_values )
        for i in range( len( output_values ) ):
            speclist[ i ] = output_values[ i ]
    else:
        for i in range( len( speclist ) ):
            speclist[ i ] = __em_drop_wrapper( ( speclist[ i ], mgii, hb ) )

    if len( speclist ) == 1:
        return speclist[ 0 ]
    return speclist

def __em_drop_wrapper( inputV ) -> Spectrum:
    from common.constants import MGII_RANGE, HB_RANGE
    spec, mgii, hb = inputV
    wls = spec.getWavelengths()
    for wl in wls:

        if mgii and hb:
            if ( MGII_RANGE[ 0 ] <= wl <= MGII_RANGE[ 1 ] ) or (  HB_RANGE[ 0 ] <= wl <= HB_RANGE[ 0 ] ):
                continue
            del spec[ wl ]
        elif mgii and not( MGII_RANGE[ 0 ] <= wl <= MGII_RANGE[ 1 ] ):
            del spec[ wl ]
        elif hb and not ( HB_RANGE[ 0 ] <= wl <= HB_RANGE[ 1 ] ):
            del spec[ wl ]
    return spec