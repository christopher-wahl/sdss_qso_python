from typing import Iterable, List, Tuple, Union


class results_pipeline:

    _results_low = None
    _results_high =  None
    _results_dict = None
    _binWidth = 0.01
    _rs_bin_low = 0.46
    _rs_bin_high = 0.82
    _shenCat = None

    def __init__( self, results_range: tuple = None, results: Union[ List or dict ] = None, binWidth: float = None,
                  rs_bin_range: tuple = None ):
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

        self._binWidth = binWidth or self._binWidth
        self._shenCat = shenCat

        self.set_range_limits( range=results_range )

        if rs_bin_range is not None:
            self._rs_bin_low, self._rs_bin_high = rs_bin_range

        if results is not None:
            try:
                self.set_results( results )
            except TypeError:
                self._typeerr( "__init__", results.__class__.__name__ )

    @staticmethod
    def _typeerr( self, func_name, type_found ):
        raise TypeError( f'{self.__class__.__name__}.{func_name}: type( results ) must be either dict or list\nType found: {type_found}' )

    def ab_v_z_data( self, get_error: bool = False ) -> Union[ Tuple[ List, List ] or Tuple[ List, List, List ] ]:
        """
        Returns the AB Magnitude vs Redshift data of the namestrings kept in .get_results(), usually intended to be used for plotting.
        If get_error = True - the only paramenter - is passed, will also return the AB Magnitude Error as a third list.

        Information is gathered by accessing shenCat.  Thus, if a namestring is not found in shenCat a notice will be printed to the terminal
        and that namestring will be skipped.

        Returns a tuple of either two lists ( redshift_list, ab_list ) or, if get_error = True,
        a tuple of three lists ( redshift_list, ab_list, ab_error_list )

        :param get_error: Defaults to False.  If True, also returns the ab_magnitude_error
        :type get_error: bool
        :rtype: tuple
        """
        if self._results_dict is None:
            raise TypeError(
                f"{self.__class__.__name__}.ab_v_z_data(): _results_dict is NoneType.  Have values been set/reduce_results run?" )

        xlist, ylist, err_list = [ ], [ ], [ ]
        for ns in self._results_dict:
            try:
                xlist.append( self._shenCat[ ns ][ 'z' ] )
                ylist.append( self._shenCat[ ns ][ 'ab' ] )
                err_list.append( self._shenCat[ ns ][ 'ab_err' ] )
            except KeyError:
                print(
                    f'{self.__class__.__name__}.ab_v_z_data: Unable to find namestring in shenCat and thus, cannot determine original redshift - will be skipped in returned dictionary\nnamestring: {ns}' )

        if get_error: return (xlist, ylist, err_list)

        return (xlist, ylist)

    def set_results( self, results: Union[ dict, list, Iterable ] ):
        from tools.list_dict import paired_list_to_dict
        if self._results_dict is not None:
            self._results_dict.clear()

        if type( results ) == dict:
            self._results_dict = results
        elif type( results ) == list or type( results ) == Iterable:
            self._results_dict = paired_list_to_dict( list( results ) )
        elif isinstance( results_pipeline, results ):
            self._results_dict = results.get_results( )
        else:
            self._typeerr( "set_results", results.__class__.__name__ )

    def set_range_limits( self, range_low: float = None, range_high: float = None, range: tuple = None ) -> None:
        if range is not None:
            self._results_low, self._results_high = range
        else:
            self._results_low = range_low or self._results_low
            self._results_high = range_high or self._results_high

    def reduce_results( self ) -> dict:
        if self._results_dict is None:
            raise TypeError( "results_pipeline.reduce_results(): _results_dict is NoneType.  Have results been set?" )
        keys = list( self._results_dict.keys( ) )
        for key in keys:
            if self._results_dict[ key ] < self._results_low or self._results_high < self._results_dict[ key ]:
                del self._results_dict[ key ]
        return self._results_dict

    def bin_results(self, binWidth = None ):
        from zbins.bin_utils import getBinString

        binWidth = binWidth or self._binWidth
        bin_dict = {}
        for ns, value in self._results_dict.items( ):
            try:
                binStr = getBinString( self._shenCat[ ns ][ 'z' ], self._rs_bin_low, self._rs_bin_high, binWidth )
            except KeyError:
                print(
                    f'{self.__class__.__name__}.bin_results: Unable to find namestring in shenCat and thus, cannot determine original redshift - will be skipped in returned dictionary\nnamestring: {ns}' )
            if binStr not in bin_dict:
                bin_dict[ binStr ] = {}
            bin_dict[ binStr ].update( { ns : value } )
        return bin_dict

    def get_results( self ) -> dict:
        return self._results_dict

    def write_results_csv(self, path : str, filename : str ) -> None:
        from fileio.list_dict_utils import namestring_dict_writer
        namestring_dict_writer( output_dict=self._results_dict, path=path, filename=filename )

    def set_bin_limits( self, rs_low: float, rs_high: float ) -> None:
        self._rs_bin_low = rs_low
        self._rs_bin_high = rs_high

class speclist_analysis_pipeline( results_pipeline ):

    __primeSpec = None
    __speclist = None
    __inputV = None

    __analysis_func = None

    def __init__( self, primeSpec, speclist, analysis_function, result_range: tuple = None, input_values: list = None,
                  binWidth=0.01 ):
        super( speclist_analysis_pipeline, self ).__init__( results_range=result_range, binWidth=binWidth )
        self.__primeSpec = primeSpec.cpy()
        self.__speclist = speclist
        self.__analysis_func = analysis_function
        self.__inputV = input_values or [ (primeSpec, spec) for spec in speclist ]

    def set_input_values( self, input_values: list ) -> None:
        self.__inputV = input_values

    def do_analysis( self, input_values: list = None, use_imap: bool = True ):
        from tools.list_dict import paired_list_to_dict
        multi_op = None
        if use_imap:
            from common.async_tools import generic_unordered_multiprocesser as multi_op
        else:
            from common.async_tools import generic_map_async_multiprocesser as multi_op

        if input_values is not None: self.set_input_values( input_values )

        results = []
        multi_op( self.__inputV, self.__analysis_func, results )
        self.set_results( paired_list_to_dict( results ) )

class redshift_ab_pipeline( results_pipeline ):

    _prime_ns = None
    _prime_z = None
    _prime_mag = None
    _prime_mag_err = None
    _n_sigma = 1 # number of sigma to extend error bars out
    _evofunction = None

    def __init__( self, primary_ns: str = None, primary_z: float = None, primary_magnitude: float = None,
                  primary_magnitude_error: float = None, ns_of_interest: Union[ list or dict ] = None ):
        """
        If primary_ns is passed, constructor will pull remianing information out of shenCat.  If the namestring cannot be found
        in shenCat, the constructor will continue trying to the remaining kwargs to variables.  Will check for any NoneType variables afterward
        and if any remain, a TypeError will be raised

        Note that ns_of_interest may be either a results_dict from another results_pipeline, a simple [ ns, ns, ... ] list or a paired tuple list [ ( ns : float ), ( ns : float ), ... ].
        As this pipeline relies only on namestrings and the data availaible in the shenCatalog

        :param primary_ns: primary namestring
        :param primary_z:
        :param primary_magnitude:
        :param primary_magnitude_error:
        :param ns_of_interest:
        :raises TypeError:
        """

        from tools.cosmo import magnitude_at_redshift
        super( redshift_ab_pipeline, self ).__init__( results_range=(None, None) )

        err = False
        if primary_ns is not None:
            try:
                self._prime_ns = primary_ns
                self._prime_z, self._prime_mag, self._prime_mag_err = self._shenCat.subkey( primary_ns, 'z', 'ab',
                                                                                            'ab_err' )
            except KeyError:
                err = True
        else:
            self._prime_ns = ""

        if err:
            self._prime_z = primary_z
            self._prime_mag = primary_magnitude
            self._prime_mag_err = primary_magnitude_error

        if self._prime_z is None or self._prime_mag is None or self._prime_mag_err is None:
            self._prime_z = self._prime_z or "NONE"
            self._prime_mag = self._prime_mag or "NONE"
            self._prime_mag_err = self._prime_mag_err or "NONE"
            raise TypeError(
                f"redshift_ab_pipeline.__init__(): NoneType values in constructor:\nprime_ns:{self._prime_ns}\nprime_z: {self._prime_z}\nprime_mag: {self._prime_mag}\nprime_mag_err: {self._prime_mag_err}" )

        self._evofunction = magnitude_at_redshift

        if ns_of_interest is not None:
            self.set_namelist( ns_of_interest )

    def get_namestring_list( self ) -> List[ str ]:
        """
        Returns the namestrings ONLY, in list form, of the reuslts_dict.
        The same as calling list( .get_results().keys() )
        :rtype: list
        """
        return list( self.get_results( ).keys( ) )

    def reduce_results( self, n_sigma  = None ) -> dict:
        if self._results_dict is None:
            raise TypeError( "redshift_ab_pipeline.reduce_results(): _results_dict is NoneType.  Have results been set?" )
        keys = list( self._results_dict.keys() )
        self._n_sigma = n_sigma or self._n_sigma
        prime_max = self._prime_mag + self._prime_mag_err * self._n_sigma
        prime_min = self._prime_mag - self._prime_mag_err * self._n_sigma
        for namestring in keys:
            z, mag, mag_err = self._shenCat.subkey( namestring, 'z', 'ab', 'ab_err' )

            mag_low = self._evofunction( prime_min, self._prime_z, z )
            mag_high = self._evofunction( prime_max, self._prime_z, z )


            if mag + mag_err < mag_low or mag_high < mag - mag_err:
                del self._results_dict[ namestring  ]
        return self._results_dict

    def plot_results( self, path, filename, debug=False ) -> None:
        from tools.plot import ab_z_plot

        return ab_z_plot( path=path, filename=filename, primary=self._prime_ns, points=self,
                          plotTitle=f"Catalog Points within Expected Evolution of {self._prime_ns} within {self._n_sigma} sigma",
                          debug=debug )

    def set_namelist( self, namelist ) -> None:
        if type( namelist ) == list and type( namelist[ 0 ] ) == str:
            # Need to mutate namelist as the expected values are either { ns : float } or [ ( ns, float ), ... ] pairs
            # However, this pipe runs entirely off the ShenCatalog and thus only needs namestrings.  Putting in AB mag for good measure
            namelist = [ (r, self._shenCat[ r ][ 'ab' ]) for r in namelist ]
        try:
            self.set_results( namelist )
        except TypeError:
            self._typeerr( "__init__", namelist.__class__.__name__, namelist.__class__.__name__ )
