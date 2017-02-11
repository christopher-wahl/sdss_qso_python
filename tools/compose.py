from collections import defaultdict
from typing import List

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

    def __join( spec: Spectrum ):
        for wl in spec:
            joined[ wl ].append( spec.get( wl ) )

    joined = defaultdict( default_factory=list )
    composite = Spectrum( ns=namestring )
    joined.update( map( __join, speclist ) )

    wavelength_list = sorted( list( joined.keys( ) ) )
    fluxlist = [ ]
    errlist = [ ]

    for wl in wavelength_list:
        fluxlist.append( mean( j[ 0 ] for j in joined[ wl ] ) )
        if (len( joined[ wl ] ) > 1):
            errlist.append( std( j[ 1 ] for j in joined[ wl ] ) )
        else:
            errlist.append( joined[ wl ][ 1 ] )

    composite.setDict( wavelength_list, fluxlist, errlist )

    return composite
