import pickle

from common.constants import BASE_CODE_PATH, join


class catalog( dict ):

    __THIS_CAT = ( -1, "" )

    SHEN_CATALOG = ( 0, "shenCat" )
    DIVIDE_CATALOG = ( 1, "divCat" )
    CHI_CATALOG = ( 2, "chiCat" )

    __BASE_CATALOG_PATH = join( BASE_CODE_PATH, "catalog" )

    __SHEN_PATH = join( __BASE_CATALOG_PATH, "shenCat.bin" )
    __DIV_PATH = join( __BASE_CATALOG_PATH, "divCat.bin" )
    __CHI_PATH = join( __BASE_CATALOG_PATH, "chiCat.bin" )

    __CAT_DICT = { SHEN_CATALOG: __SHEN_PATH, DIVIDE_CATALOG: __DIV_PATH, CHI_CATALOG: __CHI_PATH }

    def __init__( self, catalog = SHEN_CATALOG ):
        super( self.__class__, self ).__init__()
        self.__THIS_CAT = catalog

    def load( self ):
        self.update( pickle.load( open( self.__CAT_DICT[ self.__THIS_CAT ], 'rb' ) ) )

    def rewrite( self ):
        d = {}.update( self )
        pickle.dump( d, open( self.__CAT_DICT[ self.__THIS_CAT ], 'wb' ) )

    def export_text(self, path = None, filename = None ):
        import json
        from fileio.utils import dirCheck

        if path is None:
            path = join( self.__BASE_CATALOG_PATH, "text_backup" )
        if filename is None:
            filename = f"{self.__THIS_CAT[ 1 ]}.bin"

        dirCheck( path )
        with open( join( path, filename ), 'w' ) as outfile:
            outfile.write( "%s = %s" % ( self.__THIS_CAT[ 1 ], json.dumps( self, sort_keys=True, indent=4, separators=(',', ': ') ) ) )

    def keys(self):
        return list( super( catalog, self ).keys() )