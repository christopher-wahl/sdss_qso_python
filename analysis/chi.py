from typing import Dict

from spectrum import Iterable, Spectrum, Tuple


def __chi_value( prime_point: Tuple[ float, float ], sec_point: Tuple[ float, float ], n_sigma: float ) -> float:
    err = (prime_point[ 1 ] + sec_point[ 1 ]) * n_sigma
    diff = abs( prime_point[ 0 ] - sec_point[ 0 ] )
    return pow( diff, 2 ) / prime_point[ 0 ] if err > diff else 0


def chi( primary: Spectrum, secondary: Spectrum, wl_low: float = None, wl_high: float = None, n_sigma=1 ) -> float:
    """
    Simple chi^2 matching system.  This method does make any modifications to the Spectrum objects passed in.  Note that
    if no wavelegnth limitations are given, the bounds of the objects will be used.

    :param primary: Primary spectrum to be checked against 
    :type primary: Spectrum
    :param secondary: Secondary spectrum to be checked against
    :type secondary: Spectrum
    :param wl_low: Minimum wavelength to begin checking at.  Defaults to None
    :type wl_low: float
    :param wl_high: Maximum wavelegnth at which to end checking.  Defaults to None
    :type wl_high: float
    :param n_sigma: Error bound multiplier in which to define the overlap range where chi value is zero.  Defaults to 1.
    :type n_sigma: float
    :return: Chi^2 value over the two spectra
    :rtype: float
    """
    wls = set( primary.keys() ).intersection( secondary.keys() )
    if wl_low is not None:
        wls = filter( lambda x: x >= wl_low, wls )
    if wl_high is not None:
        wls = filter( lambda x: x <= wl_high, wls )
    return sum( [ __chi_value( primary[ wl ], secondary[ wl ], n_sigma ) for wl in wls ] )


def __multi_chi_wrapper( inputV: Tuple[ Spectrum, Spectrum, float, float, float ] ) -> Tuple[ str, float ]:
    primary, secondary, wl_low, wl_high, n_sigma = inputV
    return (secondary.getNS(), chi( primary, secondary, wl_low, wl_high, n_sigma ))


def multi_chi_analysis( primary: Spectrum, speclist: Iterable[ Spectrum ], wl_low: float = None, wl_high: float = None,
                        n_sigma: float = 1 ) -> Dict[ str, float ]:
    """
    A multiprocessing invoking method for a mass chi^2 analysis.  Given a primary spectrum and a wavelength range,
    run a Chi^2 check against every spectrum in the passed speclist.  Chi^2 process is handed by the analysis.chi method
    in this package.
    
    :param primary: Spectrum to be matched against
    :type primary: Spectrum
    :param speclist: Iterable of type Spectrum to be matched to primary
    :type speclist: Iterable
    :param wl_low:  Minimum wavelength to be used.  Defaults to None and thus will use individual object bounds if not passed.
    :type wl_low: float
    :param wl_high: Maximium wavelength to be used.  Same case as wl_low in default to None
    :type wl_high: float
    :param n_sigma: Error bound multiplier for defining the '0' range of the chi^2 process.  Defaults to 1.
    :type n_sigma: float
    :return: Namestring dictionary of { spectrum.getNS() : chi^2 value }
    :rtype: dict
    """
    from common.async_tools import generic_unordered_multiprocesser

    results = [ ]
    input_values = [ (primary, spec, wl_low, wl_high, n_sigma) for spec in speclist ]
    generic_unordered_multiprocesser( input_values, __multi_chi_wrapper, results )
    return dict( results )
