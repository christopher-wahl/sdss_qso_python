from common.constants import DEFAULT_SCALE_WL, DEFUALT_SCALE_RADIUS
from common.messaging import KeyErrorString


class spectrum( dict ):
    __z = 0
    __gmag = 0
    __namestring = ""

    def __init__( self, *args, **kwargs ):
        super( spectrum, self ).__init__( )
        if len( args ) == 1 and isinstance( args[ 0 ], spectrum ):
            self = args[ 0 ].cpy( )
        elif len( kwargs ) != 0:
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

    def aveFlux( self, scaleWL=None, radius=None ):
        scaleWL = scaleWL or DEFAULT_SCALE_WL
        radius = radius or DEFUALT_SCALE_RADIUS

    def cpy( self ):
        """
        Returns a deep copy of this spectra

        :return: spectra
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

    def getWavelengths( self ):
        return sorted( self.keys( ) )

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
                raise KeyError( KeyErrorString( "spectra.scale", key, val ) )

        scaleWL = scaleWL or DEFAULT_SCALE_WL
        radius = radius or DEFUALT_SCALE_RADIUS

        if scaleSpec is not None:
            scaleflux = scaleSpec.aveFlux( scaleWL, radius )
        elif scaleflux is None:
            raise TypeError( "No scaleflux value determined in spectra.scale( **kwargs )" )

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
                raise KeyError( KeyErrorString( "spectra.scale", key, val ) )

        scaleWL = scaleWL or DEFAULT_SCALE_WL
        radius = radius or DEFUALT_SCALE_RADIUS

        if scaleSpec is not None:
            scaleflux = scaleSpec.aveFlux( scaleWL, radius )
        elif scaleflux is None:
            raise TypeError( "No scaleflux value determined in spectra.scaleFactor( **kwargs )" )

        return scaleflux
