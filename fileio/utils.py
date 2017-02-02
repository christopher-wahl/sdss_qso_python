from re import search

from common.constants import abspath, join, os


def dirCheck( *args ):
    """
    Checks if a given path exists.  If not, creates the folders to it.

    join( *args ) will be called on all passed parameters before checking

    :param args: string list of /path/to/dir
    :type args: list
    :return: None
    :rtype: None
    """
    path = join( *args )
    if not os.path.isdir( path ):
        os.makedirs( path )

def extCheck( extention ):
    """
    Ensures a file extention includes the leading '.'

    :param extention: file extention
    :type extention: str
    :return: Properly formatted file extention
    :rtype: str
    """
    if extention[ 0 ] != '.':
        extention = '.' + extention
    return extention

def fileCheck( path, filename ):
    if os.path.isfile( abspath( join( path, filename ) ) ):
        return True
    return False

def findNamestring( inputString ):
    """
    Uses regular expressions to find MJD-Plate-Fiber string.

    If none is found, raises a ValueError

    :param inputString: given string containing a namestring
    :type inputString: str
    :rtype: str
    :return: First instance of namestring format
    :raises: ValueError
    """
    try:
        return search( r'\d{5}-\d{4}-\d{3}', inputString ).group( 0 )
    except:
        raise ValueError( "Unable to find namestring in the given inputString.\ninputString: %s" % inputString )

def fns( inputString ):
    """
    Shortcut call to utils.findNamestring( inputString )

    :param inputString: String to be seached for namestring format
    :type inputString: str
    :return: Namestring
    :rtype: str
    """
    return findNamestring( inputString )

def getFiles( path, extention = None ):
    """
    Returns a list of all files within the given path.

    If extention is specified, will only return files with said extention

    :param path: /path/to/directory/of/interest
    :param extention: File extention of interest.  If not specified, all files in directory are returned
    :type path: str
    :type extention: str
    :return: List of str() files in directory.  If extention is specified, only those files with that file extention are returned.
            Note that this list will NOT include the /path/to/ in the file names - merely the names themselves
    :rtype: list
    """
    extention = extCheck ( extention ) if extention is not None else ''
    return[ f for f in os.listdir( path ) if ( os.path.isfile( os.path.join( path, f ) ) and (os.path.splitext( f )[ 1 ].endswith( extention ))) ]

def ns2f( namestring, extention ):
    """
    Shortcut call for utils.namestringToFilename( namestring, extention )

    :param namestring: leading filename
    :param extention:  file extention
    :type namestring: str
    :type str
    :return: concatated filename
    :rtype str
    """
    return namestringToFilename( namestring, extention )

def namestringToFilename( namestring, extention ):
    """
    Concatates namestring & extention, passing extention through extCheck first

    :param namestring: leading filename
    :param extention:  file extention
    :type namestring: str
    :type str
    :return: concatated filename
    :rtype str
    """
    return namestring + extCheck( extention )