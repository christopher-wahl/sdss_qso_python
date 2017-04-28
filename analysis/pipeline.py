from typing import Callable, Dict, Iterable, Optional, Tuple, Union

from common.constants import CHI_BASE_MAG
from spectrum import Spectrum, flux_from_AB


class analysis_pipeline:
    """
    Simplified anaylsis pipe for comparing one Spectrum to a list of others via some function.
    
    This analysis function must take in a single item - a tuple of objects which will be unpacked within the function
    itself - perform the action, and return a tuple of ( unique identifier, value ).  Generally, this will be  a 
    ( namestring, float ).  These values will be joined to form a dictionary of { unique identifier : value } and stored
    in the results.  This process is begun by calling .do_analysis()
    
    These results will be the complete result set for every point in the input_values list.  They may be reduced to the
    provided range_limits passed at initialization by calling reduce_results().  Alternatively, a custom reduction
    reduction method may be applied by calling .reduce_results( reduction_function ).
    
    This custom reduction method must take in a tuple which will correspond to the ( key, value ) tuple iterated from
    the results.items() dictionary, and return a boolean-identifiable value. If True, the  key : value will be kept.
    Elsewise, it will be dropped.
       
    Both before and after reduce_results() is called, get_results() can be called and the results dictionary will be
    returned.  If do_analysis() has not yet been called, both of these methods will raise an AssertionError. 
    """
    __input_list = None
    __range_limits = None
    __analysis_function = None
    __results = None

    def __init__( self, input_list: Iterable,
                  analysis_function: Callable[ [ object ], Tuple[ str, float ] ],
                  range_limits: Tuple[ Optional[ float ], Optional[ float ] ] = (None, None) ):
        """
        analysis_pipeline initializer.  See class comments for further information.
        
        The input_list should be a list of tuples.  Each tuple will be passed to the analysis_function via the
        generic_unordered_multiprocessor method in tools.async_tools.
        
        The analysis_function should accept one arugment; a tuple of all the arguments being passed.  It should unpack
        this tuple within the function, perform the operation and provide an output in the form of ( namestring, float ).
        
        do_analysis() will perform the actual anaylsis, calling this analysis_fucntion and formingt the results
        dictionary.
        
        These values will be transformed into a dictionary of { namestring : float }, which will be stored as the set
        of results.
        
        :param input_list: Values to be passed to analysis_function.
        :type input_list: Iterable
        :param analysis_function: Method which accepts a single tuple from input_list, returns a tuple of ( str, float )
        :type analysis_pipeline: Callable
        :param range_limits: ( Min, Max ) limitations to be used of the float returned value from analysis_function when
        reduce_results() is called.
        :type range_limits: tuple
        """
        self.__input_list = input_list
        self.__range_limits = range_limits
        self.__analysis_function = analysis_function

    def do_analysis( self ):
        """
        Start the analysis_function processing.
        :return: 
        """
        assert self.__primeSpec is not None and self.__input_list is not None and self.__analysis_function is not None and self.__range_limits is not None
        from tools.async_tools import generic_unordered_multiprocesser
        from tools.list_dict import paired_list_to_dict

        results = [ ]
        generic_unordered_multiprocesser( input_values=self.__input_list, multi_function=self.__analysis_function,
                                          output_values=results )
        self.__results = paired_list_to_dict( results )

    def reduce_results( self, reduction_fuction: Optional[ Callable[ [ Tuple[ str, float ] ], bool ] ] = None ) -> dict:
        """
        Reduces the results after the do_analysis() process has been completed.  The values will be both returned at the
        completion of this method, as well as stored, overwriting the previous results from do_analysis().
        
        The stored results value are accessible from the .get_results() method.  If reduce_results() has not been run,
        the unreduced results from do_analysis() will be returned.
        
        If reduction_function is not passed, the limitations provided to the object at initialization will be used.
        
        Otherwise, can make use of a custom reduction function.  Custom method must take in a tuple( str, float ), as it
        will be called by filter() and passed the values iterated from the results.items() dictionary.  This method must
        return a boolean-interpretable value.  True-returning values will keep the item, False will remove it.
        
        Note that any limiting values must be imposed by this reduction function.
        
        :param reduction_fuction: Custom method to determine reduction of results.  Must accept a tuple of ( str, float )
        :type reduction_fuction: Callable
        :return: reduced results
        :rtype: dict
        :raises: AssertionError
        """
        try:
            assert isinstance( self.__results, dict )
        except AssertionError:
            raise AssertionError(
                    "pipeline:  Results dictonary has not been assigned a value.  Has do_analysis() been called?" )

        if reduction_fuction is not None:
            self.__results = dict( filter( reduction_fuction, self.__results.items() ) )
        else:
            low_limit, high_limit = self.__range_limits
            if low_limit is not None:
                self.__results = filter( lambda x: x[ 1 ] >= low_limit, self.__results.items() )
            if high_limit is not None:
                self.__results = filter( lambda x: x[ 1 ] <= high_limit,
                                         self.__results.items() if isinstance( self.__results,
                                                                               dict ) else self.__results )
            self.__results = dict( self.__results )
        return self.__results

    def get_results( self ) -> Dict[ str, float ]:
        """
        Returns the stored results from do_analysis() or reduce_results().  If reduce_results() has been been run, the
        full result dictionary from do_analysis() is returned.  Otherwise, only the reduced result dictionary will
        be accessible.
        
        :return: Analysis/Reduced analysis results
        :rtype: dict
        :raises: AssertionError
        """
        try:
            assert isinstance( self.__results, dict )
        except AssertionError:
            raise AssertionError(
                    "pipeline:  Results dictonary has not been assigned a value.  Has do_analysis() been called?" )

        return self.__results


def get_chi_analysis_pipeline( primary_spectrum: Union[ Spectrum, str ], speclist: Iterable[ Union[ Spectrum, str ] ],
                               wl_limits: Tuple[ float, float ], maximum_chi_value: float, n_sigma: float = 1,
                               scale_AB_mag: float = CHI_BASE_MAG ) -> analysis_pipeline:
    """
    Prebuilt method for forming a chi^2 analysis pipeline with the analysis_pipeline class.
    
    primary_spectrum and speclist iterable values may be passed as Spectrum objects or as namestrings (in which case
    their rest frame spectra will be loaded from disk via fileio methods). WARNING:  Only the first value in speclist
    will be checked for typing.  If str, the entire speclist will be passed to async_rspec_scaled for loading.  Else,
    the entire speclist will be passed to multi_scale for scaling.  All spectra are scaled to the primary spectrum,
    which is itself scaled to an AB magnitude of scale_AB_mag (which defaults to common.constants.CHI_BASE_MAG).
    
    The input_values is formed given the passed wl_limits and chi_pipeline_function is used as the analysis.chi wrapper.
    
    The pipeline object, prepared with range_limits of ( None, maximum_chi_value ) is returned.  No analysis is
    performed; neither do_analysis() nor reduce_results() are called. 
    
    :param primary_spectrum: Spectrum to perform chi^2 matching to.  May be a namestring or Spectrum object
    :type primary_spectrum: str or Spectrum
    :param speclist: Iterable of Spectrum or namestring objects to match to primary
    :type speclist: Iterable
    :param wl_limits: tuple of ( wl_low, wl_high ) range to match against.
    :type wl_limits: tuple
    :param maximum_chi_value: Maximum value of chi^2 result to be used in the event of calling reduce_results()
    :type maximum_chi_value: float
    :param n_sigma: Uncertainty multiplier to be passed to analysis.chi.  Defaults to 1.
    :type n_sigma: float
    :param scale_AB_mag: AB magnitude to scale all objects to.  Defaults to common.constants.CHI_BASE_MAG
    :type scale_AB_mag: float
    :return: Prepared chi^2 analysis pipeline.
    :rtype: analysis_pipeline
    """
    from fileio.spec_load_write import async_rspec_scaled, rspecLoader
    from fileio.utils import fns

    from spectrum.utils import mutli_scale
    if isinstance( primary_spectrum, str ):
        primary_spectrum = rspecLoader( fns( primary_spectrum ) )
    primary_spectrum.scale( scaleflux=flux_from_AB( scale_AB_mag ) )
    if not isinstance( speclist, list ):
        speclist = list( speclist )
    if not isinstance( speclist[ 0 ], Spectrum ):
        speclist = async_rspec_scaled( speclist, primary_spectrum )
    else:
        speclist = mutli_scale( primary_spectrum, speclist )

    input_values = [ (primary_spectrum, spec, wl_limits[ 0 ], wl_limits[ 1 ], n_sigma) for spec in speclist ]
    return analysis_pipeline( input_values, chi_pipeline_function,
                              (None, maximum_chi_value) )


def chi_pipeline_function( input_value: Tuple[ Spectrum, Spectrum, float, float, float ] ) -> Tuple[ str, float ]:
    """
    Wrapper for the analysis.chi method for use in an analysis_pipeline.
    
    :param input_value: tuple of ( primary_spectrum, secondary_spectrum, wl_low_lit, wl_high_limit, n_sigma ) to be passed to chi() method, in that order.
    :type input_value: tuple
    :return: tuple of ( seconday_spectrum.getNS(), float )
    :rtype: tuple
    """
    from analysis.chi import chi
    primary, seconday, wl_low, wl_high, n_sigma = input_value
    return (seconday.getNS(), chi( primary, seconday, wl_low, wl_high, n_sigma ))
