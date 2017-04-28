from typing import Callable, Union

from numpy import diag, sqrt
from scipy.optimize import curve_fit

from spectrum import Iterable, Spectrum, Tuple


def __linear_func( x: float, m: float, b: float ) -> float:
    return m * x + b


def __quad_func( x: float, a: float, b: float, c: float ) -> float:
    return a * (x ** 2) + b * x + c


def __log10_fit( x: float, a: float, b: float ) -> float:
    from numpy import log10
    return a * log10( x ) + b


def generic_fit( fit_function: Callable, x_data: Iterable[ float ], y_data: Iterable[ float ],
                 get_uncertainty: bool = False ) -> tuple:
    """
    Attempts a fit to whatever callable fit_function is passed.  The function must be of the form f( x, ... ).  Returned
    tuple will be in the order of constants in the method header after the first, x, value.
    
    If get_uncertainty is passed, returns a tuple of ( fit values, uncertainty of fit values )
    
    :param fit_function: 
    :type fit_function: Callable
    :param x_data: 
    :type x_data: Iterable
    :param y_data: 
    :type y_data: Iterable
    :param get_uncertainty:
    :type get_uncertainty: bool
    :return:
    :rtype: tuple
    """
    coeff, pcov = curve_fit( fit_function, x_data, y_data )
    uncert = sqrt( diag( pcov ) )
    return tuple( coeff ) if not get_uncertainty else (tuple( coeff ), tuple( uncert ))


def generic_linear_fit( x_data: Iterable[ float ], y_data: Iterable[ float ], get_uncertainty: bool = False ) -> Union[
    Tuple[ float, float ], Tuple[ Tuple[ float, float ], Tuple[ float, float ] ] ]:
    """
    Performs a generic linear fit to x and y data.  
    
    returns a tuple of ( m, b )
    
    If get_uncertainty is True, will return the uncertainties of the fit values as well.  The returned value will be
    ( ( m, b ), ( uncertainty of m, uncertainty of b ) )
    
    :param x_data: 
    :type x_data: Iterable
    :param y_data: 
    :type y_data: Iterable
    :param get_uncertainty:
    :type get_uncertainty: bool
    :return:
    :rtype: tuple
    """
    return generic_fit( __linear_func, x_data, y_data, get_uncertainty )


def generic_log10_fit( x_data: Iterable[ float ], y_data: Iterable[ float ], get_uncertainty: bool = False ) -> Union[
    Tuple[ float, float ], Tuple[ Tuple[ float, float ], Tuple[ float, float ] ] ]:
    """
    Performs a generic log10 fit to x and y data. for the form a * log10( x ) + b   

    returns a tuple of ( a, b )

    If get_uncertainty is True, will return the uncertainties of the fit values as well.  The returned value will be
    ( ( a, b ), ( uncertainty of a, uncertainty of b ) )

    :param x_data: 
    :type x_data: Iterable
    :param y_data: 
    :type y_data: Iterable
    :param get_uncertainty:
    :type get_uncertainty: bool
    :return:
    :rtype: tuple
    """
    return generic_fit( __log10_fit, x_data, y_data, get_uncertainty )


def generic_quad_fit( x_data: Iterable[ float ], y_data: Iterable[ float ], get_uncertainty: bool = False ) -> Union[
    Tuple[ float, float, float ], Tuple[ Tuple[ float, float, float ], Tuple[ float, float, float ] ] ]:
    """
    Performs a generic quadaratic fit to x and y data.  Returns a tuple of ( a, b, c ) for ax^2 + bx + c
     
    If get_uncertainty is True, will return the uncertainties of the fit values as well.  The returned value will be
    ( ( a, b, c ), ( uncertainty of a, uncertainty of b, uncertainty of c ) )
    
    :param x_data: 
    :type x_data: Iterable
    :param y_data: 
    :type y_data: Iterable
    :param get_uncertainty:
    :type get_uncertainty: bool
    :return:
    :rtype: tuple
    """
    return generic_fit( __quad_func, x_data, y_data, get_uncertainty )


def spectrum_linear_fit( spec: Spectrum, wl_low: float = None, wl_high: float = None ) -> Tuple[ float, float ]:
    """
    Applies a linear fit to a Specturm over the specified wavelength range.  If no wl_ values are passed,
    the entirely of the spectrum range is used.
    
    Returns a tuple of ( m, b ) for:
    
    Flux Density = m * Wavelength + b
    
    :param spec: Spectrum to slope fit
    :type spec: Spectrum
    :param wl_low: Low limit of wavelength range.  Defaults to None
    :type wl_low: float
    :param wl_high: Upper limit of wavelength range.  Defaults to None
    :type wl_high: float
    :return: ( m, b ) 
    :rtype: tuple
    """
    wls = spec.getWavelengths()
    if wl_low is not None:
        wls = filter( lambda wl: wl >= wl_low, wls )
    if wl_high is not None:
        wls = filter( lambda wl: wl <= wl_high, wls )
    fluxdata = [ spec.getFlux( wl ) for wl in wls ]  # Can't use .getFluxlist here in clase wavelength limits used
    return generic_linear_fit( wls, fluxdata )
