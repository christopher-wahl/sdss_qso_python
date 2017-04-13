from typing import List, Tuple

from common.constants import DEFAULT_SCALE_RADIUS, DEFAULT_SCALE_WL, linesep
from common.messaging import KeyErrorString


class Spectrum( dict ):
    __z = float( )
    __gmag = float( )
    __namestring = str( )

    def __init__( self, *args, **kwargs ):
        super( Spectrum, self ).__init__( )
        if len( kwargs ) != 0:
            for arg, val in kwargs.items( ):
                if arg in 'z':
                    self.__z = val
                elif arg in 'gmag':
                    self.__gmag = val
                elif arg in "namestring" or arg in "ns":
                    self.__namestring = val
                elif arg in "dict":
                    self.update( val )
                else:
                    raise KeyError( KeyErrorString( "specturm constructor", arg, val ) )
        return

    def __repr__( self ):
        return '%s  z: %s   gmag: %s\n%s    %s' % (
            self.getNS( ), self.getRS( ), self.getGmag( ), self.getWavelengths( )[ 0 ], self.getWavelengths( )[ -1 ])

    def abErr( self, wl_range: Tuple[ float, float ] = (None, None) ) -> float:
        """
        Determines the AB magnitude at every point within the wl_range individually.
        Returns the standard deviation of that value.

        :param wl_range: ( low, high ), defaults to DEFAULT_SCALE_WL +/- DEFAULT_SCALE_RADIUS
        :type wl_range: tuple
        :return: AB Magnitude error
        :rtype: float
        """
        from numpy import log10, nanstd
        minwl = wl_range[ 0 ] or DEFAULT_SCALE_WL - DEFAULT_SCALE_RADIUS
        maxwl = wl_range[ 1 ] or DEFAULT_SCALE_WL + DEFAULT_SCALE_RADIUS
        err_v = list( )
        for wl in self.getWavelengths( ):
            if minwl <= wl <= maxwl:
                f_v = 3.34E4 * pow( wl, 2 ) * 1E-17 * self[ wl ][ 0 ]
                if f_v < 0:
                    continue
                err_v.append( -2.5 * log10( f_v ) + 8.9 )
        return float( nanstd( err_v ) )

    def align(self, wlList ):
        wls = self.getWavelengths()
        for wl in wls:
            if wl not in wlList:
                del self[ wl ]

    def alignToSpec(self, spec ):
        self_wls = set( self.getWavelengths() )
        spec_wls = set( spec.getWavelengths() )

        for wl in ( self_wls - spec_wls ):
            del self[ wl ]
        for wl in ( spec_wls - self_wls ):
            del spec[ wl ]

    def aveFlux( self, central_wl=None, radius=None ):
        central_wl = central_wl or DEFAULT_SCALE_WL
        radius = radius or DEFAULT_SCALE_RADIUS
        s = 0
        n = 0
        for wl in self.getWavelengths():
            if(central_wl - radius <= wl <= central_wl + radius):
                s += self.getFlux( wl )
                n += 1
        try:
            return s / n
        except ZeroDivisionError as e:
            print(
                f"Spectrum.aveFlux: ZeroDivisionError - unable to determine average flux for spectrum {self.getNS() }.  Is the region of interest loaded?" )
            print( f"central_wl{central_wl}     radius: {radius}" )
            print( self, flush=True )
            from sys import exit
            exit( 1 )

    def aveErr( self, wl_low: float = None, wl_high: float = None, wl_range: Tuple[ float, float ] = None ) -> float:
        if wl_range is not None:
            wl_low, wl_high = wl_range
        elif wl_low is None or wl_high is None:
            raise ValueError(
                f"Spectrum.aveErr: Need low and high wl values, or need a wl_range{linesep}wl_low: {wl_low} - wl_high:{wl_high}{linesep}{self}" )
        n = 0
        err = 0
        for wl in self:
            if wl_low <= wl <= wl_high:
                err += self.getErr( wl )
                n += 1
        return err / n if n != 0 else -1

    def bin( self, step: float = 1, init_wl: float = None ) -> None:
        wls = self.getWavelengths()
        wlslist = []
        flxlist = []
        errlist = []

        lowIndex, highIndex = 0, 1

        while( lowIndex < len( wls ) - 1 ):
            lowWL = wls[ lowIndex ]
            highWL = wls[ highIndex ]
            newWL = init_wl if init_wl is not None else int( lowWL )
            while( highWL - newWL < step ):
                highIndex += 1
                if( highIndex == len( wls ) ):
                    break
                else:
                    highWL = wls[ highIndex ]
        #highIndex -= 1
        #highWL = wls[ highIndex ]
            fluxsum, errsum = 0, 0
            for i in range( lowIndex, highIndex, 1 ):
                lowWL = wls[ i ]
                fluxsum += self.getFlux( lowWL )
                errsum += self.getErr( lowWL )
            fluxsum /= ( highIndex - lowIndex )
            errsum /= ( highIndex - lowIndex )

            flxlist.append( fluxsum )
            errlist.append( errsum )
            wlslist.append( newWL )
            lowIndex = highIndex
            highIndex += 1
        self.setDict( wlslist, flxlist, errlist )
        return self

    def cpy( self ):
        """
        Returns a deep copy of this spectrum

        :return: spectrum
        """
        from copy import deepcopy
        return deepcopy( self )

    def cpy_info( self ):
        """
        Resturns a spectrum devoid of wl/flux data, but with the same namestring, redshift and gmag as this one.

        :rtype: Spectrum
        """
        spec = Spectrum( ns=self.getNS( ), z=self.getRS( ), gmag=self.getGmag( ) )
        return spec

    def dim_to_ab( self, to_mag_ab: float, scale_wl=DEFAULT_SCALE_WL ) -> None:
        """
        Determines the desired flux that would be exhibited at a given AB Magnitude and wavelength,
        then passes that value to the Spectrum.scale() method, scaling the spectrum to that flux density
        :param to_mag_ab: AB Magnitude desired to be dimmed to
        :param scale_wl: Wavelength to scale around.  Defaults to common.constants.DEFAULT_SCALE_WL
        :type to_mag_ab: float
        :type scale_wl: float
        :return: None
        :rtype: None
        """
        exponent = (8.9 - to_mag_ab) / 2.5
        f_v = pow( 10, exponent )
        f_lambda = f_v / (3.34E4 * 1E-17 * pow( scale_wl, 2 ))
        self.scale( scaleflx=f_lambda )

    def getFlux( self, wavelength ):
        return self[ wavelength ][ 0 ]

    def getErr( self, wavelength ):
        return self[ wavelength ][ 1 ]

    def getFluxlist( self ):
        return [ self.getFlux( wl ) for wl in self.getWavelengths( ) ]

    def getErrList( self ):
        return [ self.getErr( wl ) for wl in self.getWavelengths( ) ]

    def getGmag( self ) -> float:
        """
        Returns the magnitude in G filter of the spectrum

        :rtype: float
        """
        return self.__gmag

    def getNS( self ) -> str:
        """
        Returns the namestring of the spectrum object
        :rtype: str
        """
        return self.__namestring

    def getRS( self ) -> float:
        """
        Returns the stored redshift of the spectrum

        :rtype: float
        """
        return self.__z

    def getWavelengths( self ) -> List[ float ]:
        return sorted( self.keys( ) )

    def isAligned(self, spec ) -> bool:
        return spec.keys() == self.keys()

    def lineDict( self, wavelength ) -> dict:
        return { 'wavelength': wavelength, 'flux density': self.getFlux( wavelength ),
                 'error': self.getErr( wavelength ) }

    def lineDictList( self ) -> List[ dict ]:
        return [ self.lineDict( wl ) for wl in self.getWavelengths( ) ]

    def magAB( self, wl_range: Tuple[ float, float ] = (None, None) ) -> float:
        """
        Determines the average AB Magnitude over the given band of interest.

        If wl_range is not specified, defaults to common.constants DEFAULT_SCALE_WL +/- DEFAULT_SCALE_RADIUS

        :param wl_range: Band range over which to determine AB magntiude
        :type wl_range: tuple
        :return: AB Magnitude
        :rtype: float
        """
        from numpy import mean, log10

        minwl = wl_range[ 0 ] or DEFAULT_SCALE_WL - DEFAULT_SCALE_RADIUS
        maxwl = wl_range[ 1 ] or DEFAULT_SCALE_WL + DEFAULT_SCALE_RADIUS

        f_vlist = list( )
        f_v = None
        for wl in self.getWavelengths( ):
            if minwl <= wl <= maxwl:
                f_v = 3.34E4 * pow( wl, 2 ) * 1E-17 * self[ wl ][ 0 ]
                f_vlist.append( f_v )
        try:
            f_v = mean( f_vlist )
        except RuntimeWarning as e:
            print(
                f"Spectrum.magAB(): {self.getNS()} got a RuntimeWarning when trying to form flux mean: {f_v} \n fluxlist: {f_vlist}" )
            raise e
        return -2.5 * log10( f_v ) + 8.9

    def nearest( self, wavelength: float ) -> float:
        """
        Simple wrapper for tools.find_nearest_wavelength.  Passes this Spectrum's sorted wavelength list (via
        Spectrum.getWavelengths()) and wavelength to find_nearest_wavelength, and returns that value.

        :param wavelength: Wavelength of interest
        :type wavelength: float
        :return: Value of the nearest wavelength
        :rtype: float
        """
        from spectrum.utils import find_nearest_wavelength
        return find_nearest_wavelength( self.getWavelengths( ), wavelength )

    def setDict( self, wavelengthList, fluxList, errList ):
        """
        Replace the current wavelength dictionary with the data passed to method.

        :param wavelengthList: wavelength values
        :param fluxList: flux density values
        :param errList: flux density error values
        :type wavelengthList: list
        :type fluxList: list
        :type errList: list
        :return: None
        :rtype: None
        """
        self.clear( )
        for i in range( len( wavelengthList ) ):
            self[ wavelengthList[ i ] ] = (fluxList[ i ], errList[ i ])

    def setRS(self, redshift ):
        """
        Manually set the redshift of the spectrum

        :type redshift: float
        :return: None
        """
        assert type( redshift ) == float
        self.__z = redshift

    def setNS(self, namestring : str ):
        self.__namestring = namestring

    def shiftToRest( self, z: float = None ) -> None:
        if z is None:
            z = self.__z

        wls = [ wl / (1 + z) for wl in self.getWavelengths( ) ]
        fluxlist = self.getFluxlist( )
        errlist = self.getErrList( )
        self.clear( )
        for i in range( len( wls ) ):
            self[ wls[ i ] ] = (fluxlist[ i ], errlist[ i ])

    def scale( self, **kwargs ):
        """
        Possible kwargs:

        scalewl: central scale wavelength to scale around; defaults to common.constants.DEFAULT_SCALE_WL

        radius: radius to use for average flux determination; defaults to common.constants.DEFAULT_SCALE_RADIUS

        scaleflx: flux of spectrum scaling to

        spectrum: Make use of a spectrum to directly determine scaleflx.
        
        ab: AB Magntiude to scale the spectrum to over the default range.

        :param kwargs:
        :type kwargs: dict
        :return:
        """
        scaleWL = None
        scaleflux = None
        scaleSpec = None
        radius = None

        for key, val, in kwargs.items( ):
            key = key.lower( )
            if key in [ 'scalewl', 'sw' ]:
                scaleWL = val
            elif key in [ 'scaleflux', 'scaleflx', 'sf' ]:
                scaleflux = val
            elif key in [ 'specturm', 'spec' ]:
                assert isinstance( scaleSpec, Spectrum )
                scaleSpec = val
            elif key in [ 'radius', 'r' ]:
                radius = val
            elif key in [ 'ab' ]:
                from spectrum.utils import flux_from_AB
                scaleflux = flux_from_AB( val )
            else:
                raise KeyError( KeyErrorString( "spectrum.scale", key, val ) )

        scaleWL = scaleWL or DEFAULT_SCALE_WL
        radius = radius or DEFAULT_SCALE_RADIUS

        if scaleSpec is not None:
            scaleflux = scaleSpec.aveFlux( scaleWL, radius )
        elif scaleflux is None:
            raise TypeError( "No scaleflux value determined in spectrum.scale( **kwargs )" )

        scalar = scaleflux / self.aveFlux( scaleWL, radius )
        if scalar == 1.0: return self
        for wl in self:
            self[ wl ][ 0 ] *= scalar
            self[ wl ][ 1 ] *= scalar
        return self

    def scaleFactor( self, **kwargs ) -> float:
        scaleWL = None
        scaleflux = None
        scaleSpec = None
        radius = None

        for key, val, in kwargs.items( ):
            key = key.lower( )
            if key in [ 'scalewl', 'sw' ]:
                scaleWL = val
            elif key in [ 'scaleflux', 'scaleflx', 'sf' ]:
                scaleflux = val
            elif key in [ 'specturm', 'spec' ]:
                scaleSpec = val
            elif key in [ 'radius', 'r' ]:
                radius = val
            else:
                raise KeyError( KeyErrorString( "spectrum.scale", key, val ) )

        scaleWL = scaleWL or DEFAULT_SCALE_WL
        radius = radius or DEFAULT_SCALE_RADIUS

        if scaleSpec is not None:
            scaleflux = scaleSpec.aveFlux( scaleWL, radius )
        elif scaleflux is None:
            raise TypeError( "No scaleflux value determined in spectrum.scaleFactor( **kwargs )" )

        return scaleflux

    def trim( self, wlLow: float = None, wlHigh: float = None, wl_range=None ):
        if wl_range is not None:
            wlLow, wlHigh = wl_range
        for wl in self.getWavelengths():
            if wlLow is not None and wl < wlLow:
                del self[ wl ]
            elif wlHigh is not None and wlHigh < wl:
                del self[ wl ]

    def wl_flux_plotlist(self) -> List[ Tuple[ float, float ] ]:
        return [ ( wl, self[ wl ][ 0 ] ) for wl in self.getWavelengths() ]

    def plot( self, path : str, color : str = "royalblue", debug : bool = False ) -> None:
        from tools.plot import spectrum_plot
        from fileio.utils import dirCheck
        dirCheck( path )
        spectrum_plot( spec = self, path = path, filename = self.getNS( ), color = color, debug = debug )
