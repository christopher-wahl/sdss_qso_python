from tools import paired_list_to_dict


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
            self._results_dict = results
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
            binStr = getBinString( self._shenCat[ ns ][ 'z' ], self._rs_bin_low, self._rs_bin_high, binWidth )
            if binStr not in bin_dict:
                bin_dict[ binStr ] = {}
            bin_dict[ binStr ].update( { ns : value } )
        return bin_dict

    def get_results( self ):
        return self._results_dict

    def set_rs_bins(self, rs_low, rs_high ):
        assert ( type( rs_low ) == float or type( rs_low ) == int ) or ( type( rs_high ) == float or type( rs_high ) == int )
        self._rs_bin_low = rs_low
        self._rs_bin_high = rs_high

class redshift_ab_pipeline( results_pipeline ):

    _primary_ns = None
    _prime_z = None
    _prime_mag = None
    _prime_mag_err = None
    _evofunction = None

    def __init__(self, primary_ns, primary_z, primary_magnitude, primary_magnitude_error, results = None ):
        from tools.cosmo import magnitude_at_redshift
        from catalog import shenCat
        shenCat.load()

        super( results_pipeline, self ).__init__()

        self._primary_ns = primary_ns
        self._prime_z = primary_z
        self._prime_mag = primary_magnitude
        self._prime_mag_err = primary_magnitude_error
        self._evofunction = magnitude_at_redshift
        self._shenCat = shenCat
        if results is not None:
            try:
                self.set_results( results )
            except TypeError:
                self._typeerr( "__init__", results.__class__.__name__ )

    def reduce_results( self ):
        if self._results_dict is None:
            raise TypeError( "redshift_ab_pipeline.reduce_results(): _results_dict is NoneType.  Have results been set?" )
        keys = list( self._results_dict.keys() )
        for namestring in keys:
            z, mag, mag_err = self._shenCat.subkey( namestring, 'z', 'ab', 'ab_err' )

            mag_low = self._evofunction( self._prime_mag - self._prime_mag_err, self._prime_z, z )
            mag_high = self._evofunction( self._prime_mag + self._prime_mag_err, self._prime_z, z )


            if( mag + mag_err < mag_low or mag_high < mag - mag_err ):
                del self._results_dict[ namestring  ]

    def plot_results(self, path, filename ):
        from tools.plot import make_line_plotitem, make_points_plotitem, ab_z_plot
        from tools.cosmo import magnitude_evolution
        from tools import paired_tuple_list_to_two_lists
        from fileio.utils import dirCheck

        dirCheck( path )

        evoLow = magnitude_evolution(  self._prime_mag - self._prime_mag_err, self._prime_z )
        evoHigh = magnitude_evolution(  self._prime_mag + self._prime_mag_err, self._prime_z )
        evo = magnitude_evolution( self._prime_mag, self._prime_z )

        abData = make_points_plotitem( *self.ab_v_z_data( self, True ), color = "royalblue", title = "Catalog Points in Range" )
        evoLow = make_line_plotitem( *paired_tuple_list_to_two_lists( evoLow ), color = "grey", title = "Upper/Lower Expected Bounds" )
        evoHigh = make_line_plotitem( *paired_tuple_list_to_two_lists( evoHigh ), color = "grey" )
        evo = make_line_plotitem( *paired_tuple_list_to_two_lists( evo ), color = "black", title = "Expected Magnitude Evolution" )

        ab_z_plot( abData, evoLow, evoHigh, evo, outpath = path, outfile = filename, plotTitle = f"Catalog Points within Expected Evolution of {self._primary_ns}" )

    @staticmethod
    def ab_v_z_data( pipeline, get_error = False ):
        if pipeline._results_dict is None:
            raise TypeError( "redshift_ab_pipeline.reduce_results(): _results_dict is NoneType.  Have results been set?" )

        xlist, ylist, err_list = [], [], []
        for ns in pipeline._results_dict:
            xlist.append( pipeline._shenCat[ ns ][ 'z' ] )
            ylist.append( pipeline._shenCat[ ns ][ 'ab' ] )
            err_list.append( pipeline._shenCat[ ns ][ 'ab_err' ] )

        if get_error: return xlist, ylist, err_list

        return xlist, ylist