from common.constants import DEFAULT_SCALE_WL, DEFUALT_SCALE_RADIUS
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

    def aveFlux( self, scaleWL=None, radius=None ):
        scaleWL = scaleWL or DEFAULT_SCALE_WL
        radius = radius or DEFUALT_SCALE_RADIUS

    def cpy( self ):
        """
        Returns a deep copy of this spectrum

        :return: spectrum
        """
        from copy import deepcopy
        return deepcopy( self )

    def getFlux( self, wavelength ):
        return self[ wavelength ][ 0 ]

    def getErr( self, wavelength ):
        return self[ wavelength ][ 1 ]

    def getFluxlist( self ):
        return [ self.getFlux( wl ) for wl in self.getWavelengths( ) ]

    def getErrList( self ):
        return [ self.getErr( wl ) for wl in self.getWavelengths( ) ]

    def getGmag( self ):
        """
        Returns the magnitude in G filter of the Spectrum

        :rtype: float
        """
        return self.__gmag

    def getNS( self ):
        """
        Returns the namestring of the Spectrum object
        :rtype: str
        """
        return self.__namestring

    def getRS( self ):
        """
        Returns the stored redshift of the Spectrum

        :rtype: float
        """
        return self.__z

    def getWavelengths( self ):
        return sorted( self.keys( ) )

    def lineDict( self, wavelength ):
        return { 'wavelength': wavelength, 'flux density': self.getFlux( wavelength ),
                 'error': self.getErr( wavelength ) }

    def lineDictList( self ):
        return [ self.lineDict( wl ) for wl in self.getWavelengths( ) ]

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
        Manually set the redshift of the Spectrum

        :type redshift: float
        :return: None
        """
        assert type( redshift ) == float
        self.__z = redshift

    def shiftToRest( self, z=None ):
        if z is None:
            z = self.__z

        wls = [ wl / (1 + z) for wl in self.getWavelengths( ) ]
        fluxlist = self.getFluxlist( )
        errlist = self.getErrList( )
        self.clear( )
        for i in range( len( wls ) ):
            self[ wls[ i ] ] = (fluxlist[ i ], errlist[ i ])

    def scale( self, **kwargs ):
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
        radius = radius or DEFUALT_SCALE_RADIUS

        if scaleSpec is not None:
            scaleflux = scaleSpec.aveFlux( scaleWL, radius )
        elif scaleflux is None:
            raise TypeError( "No scaleflux value determined in spectrum.scale( **kwargs )" )

        scalar = scaleflux / self.aveFlux( scaleWL, radius )
        if scalar == 1.0: return self
        for wl in self:
            self[ wl ] = (self[ wl ][ 0 ] * scalar, self[ wl ][ 1 ] * scalar)
        return self

    def scaleFactor( self, **kwargs ):
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
        radius = radius or DEFUALT_SCALE_RADIUS

        if scaleSpec is not None:
            scaleflux = scaleSpec.aveFlux( scaleWL, radius )
        elif scaleflux is None:
            raise TypeError( "No scaleflux value determined in spectrum.scaleFactor( **kwargs )" )

        return scaleflux

# TODO: Create bin method