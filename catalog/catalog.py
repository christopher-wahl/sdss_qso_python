import pickle

from common.constants import BASE_CODE_PATH, BASE_PROCESSED_PATH, join


class catalog( dict ):

    __THIS_CAT = ( -1, "" )
    __isLoaded = False

    SHEN_CATALOG = ( 0, "shenCat" )
    DIVIDE_CATALOG = ( 1, "divCat" ) # Format: slope, intercept, average
    CHI_CATALOG = ( 2, "chiCat" )

    __BASE_CODE_CAT_PATH = join( BASE_CODE_PATH, "catalog" )

    __SHEN_PATH = join( __BASE_CODE_CAT_PATH, "shenCat.bin" )

    __DIV_PATH = join( BASE_PROCESSED_PATH, "Catalogs", "DivCat" )
    __CHI_PATH = join( BASE_PROCESSED_PATH, "Catalogs", "ChiCat" )

    __CAT_DICT = { SHEN_CATALOG: __SHEN_PATH, DIVIDE_CATALOG: __DIV_PATH, CHI_CATALOG: __CHI_PATH }

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
        import json
        from fileio.utils import dirCheck

        if path is None:
            path = join( self.__BASE_CODE_CAT_PATH, "text_backup" )
        if filename is None:
            filename = f"{self.__THIS_CAT[ 1 ]}.json"

        dirCheck( path )
        with open( join( path, filename ), 'w' ) as outfile:
            outfile.write( "%s = %s" % ( self.__THIS_CAT[ 1 ], json.dumps( self, sort_keys=True, indent=4, separators=(',', ': ') ) ) )

    def keys(self) -> list:
        return list( super( catalog, self ).keys() )

    def load( self, namestring = None ):
        if self.__THIS_CAT == self.SHEN_CATALOG:
            self.update( pickle.load( open( self.__CAT_DICT[ self.__THIS_CAT ], 'rb' ) ) )
            self.__isLoaded = True
        elif namestring is None:
            import os
            path = os.path.split( self.__CAT_DICT[ self.__THIS_CAT ] )[ 0 ]
            if self.__THIS_CAT == self.DIVIDE_CATALOG:
                path = join( path, "DivDict.bin" )
            elif self.__THIS_CAT == self.CHI_CATALOG:
                path = join( path, "ChiDict.bin" )
            self.update( pickle.load( open( path, "rb" ) ) )
            self.__isLoaded = True
            """elif self.__THIS_CAT == self.DIVIDE_CATALOG:
            if namestring is None:
                import os
                path = os.path.split( self.__CAT_DICT[ self.__THIS_CAT ] )[ 0 ]
                path = join( path, "DivDict.bin" )
                self.update( pickle.load( open( path, "rb" ) ) )
                self.__isLoaded = True
            else:"""
        elif self.__THIS_CAT == self.DIVIDE_CATALOG:
            self.__setitem__( namestring, pickle.load( open( join( self.__CAT_DICT[ self.__THIS_CAT ], f"{namestring}-div.bin" ), 'rb' ) ) )
        elif self.__THIS_CAT == self.CHI_CATALOG:
            self.__setitem__( namestring, pickle.load( open( join( self.__CAT_DICT[ self.__THIS_CAT ], f"{namestring}-chi.bin" ), 'rb' ) ) )

    def rewrite( self ):
        if self.__THIS_CAT != self.SHEN_CATALOG:
            raise TypeError( f"catalog.rewrite(): Catalog type is not SHEN_CATALOG.  Unable to rewrite.\n__THIS_CAT: {self.__THIS_CAT}" )
        d = {}.update( self )
        pickle.dump( d, open( self.__CAT_DICT[ self.__THIS_CAT ], 'wb' ) )

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
