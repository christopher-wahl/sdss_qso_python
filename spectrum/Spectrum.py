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

    def aveFlux( self, scaleWL=None, radius=None ):
        scaleWL = scaleWL or DEFAULT_SCALE_WL
        radius = radius or DEFUALT_SCALE_RADIUS
        s = 0
        n = 0
        for wl in self.getWavelengths():
            if( scaleWL - radius <= wl <= scaleWL + radius ):
                s += self.getFlux( wl )
                n += 1
        return s / n


    def bin(self, step = 1 ):
        wls = self.getWavelengths()
        wlslist = []
        flxlist = []
        errlist = []

        lowIndex, highIndex = 0, 1
        while( lowIndex < len( wls ) - 1 ):
            lowWL = wls[ lowIndex ]
            highWL = wls[ highIndex ]
            newWL = int( lowWL )
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
        Returns the magnitude in G filter of the spectrum

        :rtype: float
        """
        return self.__gmag

    def getNS( self ):
        """
        Returns the namestring of the spectrum object
        :rtype: str
        """
        return self.__namestring

    def getRS( self ):
        """
        Returns the stored redshift of the spectrum

        :rtype: float
        """
        return self.__z

    def getWavelengths( self ):
        return sorted( self.keys( ) )

    def isAligned(self, spec ):
        return spec.keys() == self.keys()

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
        Manually set the redshift of the spectrum

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

    def trim(self, wlLow, wlHigh ):
        for wl in self.getWavelengths():
            if( wl < wlLow or wlHigh < wl ):
                del self[ wl ]

    def wl_flux_plotlist(self):
        return [ ( wl, self[ wl ][ 0 ] ) for wl in self.getWavelengths() ]