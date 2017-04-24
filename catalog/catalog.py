"""
This process package was designed to be extensible to multiple catalogs and for a time, did.  However, at one point
the basic data had to be regenerated.  The other catalogs - one for division values and another for chi^2 values - were
initially created to prevent the need to constantly re-divide and re-chi^2 test spectra.  They depended upon the data
which was regenerated, so were rendered moot after that.  Nor were they regenerated.  The basic structure here remains
as much of it is very useful to the heavily used shenCat.
"""

import pickle

from common.constants import BASE_CODE_PATH, join

"""
The RAW shencatalog.FITS file pulls the following key indecies

4: -> PLATE
5: -> FIBER
6: -> MJD

Namestring format: MJD->PLATE->FIBER: 6-4-5

128: -> LOGBH_HB_VP06
129: -> LOGBH_HB_VP06_ERR

134: -> LOGBH_MGII_S10
135: -> LOGBH_MGII_S10_ERR

    Used the BROAD - not narrow line values
89 -> LOG_LUM_MGII
90 -> LOG_LUM_MGII_ERR
93 -> EW_MGII
94 -> EW_MGII_ERR

55 -> LOG_LUM_HB
56 -> LOG_LUM_HB_ERR
59 -> EW_HB
60 -> EW_HB_ERR

142 -> Z_HW
"""

class catalog( dict ):

    __THIS_CAT = ( -1, "" )
    __isLoaded = False

    SHEN_CATALOG = ( 0, "shenCat" )

    __BASE_CODE_CAT_PATH = join( BASE_CODE_PATH, "catalog" )

    __SHEN_PATH = join( __BASE_CODE_CAT_PATH, "shenCat.bin" )

    __CAT_DICT = { SHEN_CATALOG: __SHEN_PATH }

    def __init__( self, catalog = SHEN_CATALOG ):
        super( self.__class__, self ).__init__()
        self.__THIS_CAT = catalog

    def __getitem__(self, namestring ):
        if self.__THIS_CAT == self.SHEN_CATALOG:
            if not self.__isLoaded:
                self.load()
            return self.get( namestring )
        elif self.__THIS_CAT == self.DIVIDE_CATALOG or self.__THIS_CAT == self.CHI_CATALOG:
            if not self.__isLoaded and namestring not in self:
                self.load( namestring )
            return self.get( namestring )

    def export_text(self, path = None, filename = None ):
        """
        Writes a .json copy of the shenCat.  If no path or filename are specificed, the values default to
        the backup folder in the catalog package.  It is recommended to use these default values.
        
        :param path: 
        :param filename: 
        :return: 
        """
        import json
        from fileio.utils import dirCheck

        if path is None:
            path = join( self.__BASE_CODE_CAT_PATH, "backup" )
        if filename is None:
            filename = f"{self.__THIS_CAT[ 1 ]}.json"

        dirCheck( path )
        with open( join( path, filename ), 'w' ) as outfile:
            outfile.write( "%s = %s" % ( self.__THIS_CAT[ 1 ], json.dumps( self, sort_keys=True, indent=4, separators=(',', ': ') ) ) )

    def keys(self) -> list:
        if self.__THIS_CAT == self.SHEN_CATALOG and not self.__isLoaded:
            self.load( )
        return list( super( catalog, self ).keys() )

    def load( self, namestring: str = None ) -> None:
        """
        If called with no arguments, loads the entire catalog.  If passed a namestring, loads that corresponding
        catalog.
        
        :param namestring:
        :type namestring: str
        :rtype: None
        """
        if self.__THIS_CAT == self.SHEN_CATALOG:
            self.update( pickle.load( open( self.__CAT_DICT[ self.__THIS_CAT ], 'rb' ) ) )
            self.__isLoaded = True
        elif namestring is None:
            import os
            path = os.path.split( self.__CAT_DICT[ self.__THIS_CAT ] )[ 0 ]
            with open( path, 'rb' ) as infile:
                self.update( pickle.load( infile ) )
            self.__isLoaded = True

    def rewrite( self ) -> None:
        """
        Makes a copy of the current shenCat.bin file, then writes the current shenCat variable as it stands to
        shenCat.bin using the pickle method.
        
        :rtype: None 
        """
        from shutil import copyfile
        copyfile( self.__CAT_DICT[ self.__THIS_CAT ], self.__CAT_DICT[ self.__THIS_CAT ] + '.bak' )
        if self.__THIS_CAT != self.SHEN_CATALOG:
            raise TypeError( f"catalog.rewrite(): Catalog type is not SHEN_CATALOG.  Unable to rewrite.\n__THIS_CAT: {self.__THIS_CAT}" )
        d = self.copy( )
        with open( self.__CAT_DICT[ self.__THIS_CAT ], 'wb' ) as outfile:
            pickle.dump( d, outfile )

    def subkey(self, namestring, *subkeys ):
        """
        Returns the subkey entries of a namestring entry.  If a subkey is a string, calls .lower() on it.

        Supports multiple subkeys sent in: subkey( namestring, subkey1, subkey2, subkey3 ... ).  If multiple
        keys are sent in, a list of the values are returned in the order of the passed subkeys

        Equivalent to:
        [ catalog[ namestring ][ subkey1 ], catalog[ namestring ][ subkey2 ], ... ]
        :param namestring:
        :param subkeys:
        :return:
        """
        if len( subkeys ) == 1:
            subkeys = subkeys[ 0 ]
            if type( subkeys ) == str:
                subkeys = subkeys.lower()
            return self[ namestring ][ subkeys ]

        subkeys = [ subkey.lower() for subkey in subkeys if type( subkey ) == str ]
        return [ self[ namestring ][ subkey ] for subkey in subkeys ]