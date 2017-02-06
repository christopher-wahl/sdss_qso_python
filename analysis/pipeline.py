from .tools import paired_list_to_dict

class speclist_analysis_pipeline:

    __primeSpec = None
    __speclist = None

    __analysis_func = None

    __results_pipeline = None

    def __init__(self, primeSpec, speclist, analysis_function, result_range, binWidth = 0.01 ):
        self.__primeSpec = primeSpec
        self.__speclist = speclist
        self.__analysis_func = analysis_function
        self.__results_pipeline = results_pipeline( *result_range, binWidth = binWidth )

    def do_analysis( self, use_imap = True ):
        if use_imap:
            from common.async_tools import generic_unordered_multiprocesser as multi_op
        else:
            from common.async_tools import generic_map_multiprocesser as multi_op

        results = []
        input_values = [ ( self.__primeSpec, spec ) for spec in self.__speclist ]
        multi_op( input_values, self.__analysis_func, results )
        self.__results_dict = paired_list_to_dict( results )

    def reduce_results( self ):
        self.__results_pipeline.reduce_results()


class results_pipeline:

    _results_low = None
    _results_high =  None
    _results_dict = None
    _binWidth = 0.01
    _rs_bin_low = 0.46
    _rs_bin_high = 0.82
    _shenCat = None

    def __init__(self, results_range, results = None, binWidth = None, rs_bin_range = None ):
        """

        :param results_range:
        :param results:
        :param binWidth:
        :param rs_bin_range:
        :type results_range: tuple
        :type results: list or dict
        :type binWidth: float
        :type rs_bin_range: tuple
        """
        from catalog import shenCat
        shenCat.load()

        self._results_low, self._results_high = results_range
        self._binWidth = binWidth or self._binWidth
        self._shenCat = shenCat

        if rs_bin_range is not None:
            self._rs_bin_low, self._rs_bin_high = rs_bin_range

        if results is not None:
            try:
                self.set_results( results )
            except TypeError:
                self._typeerr( "__init__", results.__class__.__name__ )

    def _typeerr( self, func_name, type_found ):
        raise TypeError( f'{self.__class__.__name__}.{func_name}: type( results ) must be either dict or list\nType found: {type_found}' )

    def set_results(self, results ):
        if type( results ) == dict:
            self._results_dict = dict
        elif type( results ) == list:
            self._results_dict = paired_list_to_dict( results )
        else:
            self._typeerr( "set_results", results.__class__.__name__ )

    def reduce_results( self ):
        if self._results_dict is None:
            raise TypeError( "results_pipeline.reduce_results(): _results_dict is NoneType.  Have results been set?" )
        keys = self._results_dict.keys( )
        for key in keys:
            if self._results_dict[ key ] < self._results_low or self._results_high < self._results_dict[ key ]:
                del self._results_dict[ key ]

    def bin_results(self, binWidth = None ):
        from zbins.bin_utils import getBinString

        binWidth = binWidth or self._binWidth
        bin_dict = {}
        for ns, value in self._results_dict.items( ):
            binStr = getBinString( self._shenCat[ ns ], self._rs_bin_low, self._rs_bin_high, self._binWidth )
            if bin_dict[ binStr ] is None:
                bin_dict[ binStr ] = {}
            bin_dict[ binStr ].update( { ns : value } )
        return bin_dict

    def get_results( self ):
        return self._results_dict

class redshift_ab_pipeline( results_pipeline ):

    _prime_z = None
    _prime_mag = None
    _prime_mag_err = None
    _evofunction = None

    def __init__(self, primary_z, primary_magnitude, primary_magnitude_error, results = None ):
        from .cosmo import magnitude_at_redshift
        super( results_pipeline, self ).__init__()

        self._prime_z = primary_z
        self._prime_mag = primary_magnitude
        self._prime_mag_err = primary_magnitude_error
        self._evofunction = magnitude_at_redshift
        try:
            self.set_results( results )
        except TypeError:
            self._typeerr( "__init__", results.__class__.__name__ )

    def reduce_results( self ):
        if self._results_dict is None:
            raise TypeError( "redshift_ab_pipeline.reduce_results(): _results_dict is NoneType.  Have results been set?" )
        keys = self._results_dict.keys()
        for namestring in keys:
            z = self._shenCat.subkey( namestring, 'z' )
            mag, mag_err = self._shenCat.subkey( namestring, 'ab', 'ab_err' )

            mag_low = self._evofunction( self._prime_mag - self._prime_mag_err, self._prime_z, z )
            mag_high = self._evofunction( self._prime_mag + self._prime_mag_err, self._prime_z, z )

            if mag - mag_err < mag_low or mag_high < mag + mag_err:
                del self._results_dict[ namestring  ]