from spectrum import Spectrum, align_wavelengths


def divide( numerator: Spectrum, denominator: Spectrum, wl_low: float = None, wl_high: float = None ) -> Spectrum:
    """
    Performs a point-by-point division of the numerator spectrum by the denominator spectrum.  If wavelength ranges
    are not specificed, will use the entirely of the overlapping spectra.
     
    :param numerator: 
    :type numerator: Spectrum
    :param denominator: 
    :type denominator: Spectrum
    :param wl_low: 
    :type wl_low: float
    :param wl_high: 
    :type wl_high: float
    :return: 
    :rtype: Spectrum
    """
    wls = align_wavelengths( denominator, numerator, wl_low, wl_high )
    divided = Spectrum()

    for wl in wls:
        n, n_e = numerator[ wl ]
        d, d_e = denominator[ wl ]
        flux = n / d
        err = (pow( n_e / d, 2 ) + pow( n / (d ** 2) * d_e, 2 )) ** (0.5)
        divided[ wl ] = (flux, err)

    return divided
