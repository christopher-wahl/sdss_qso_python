import pickle
from csv import DictReader, DictWriter

from common.constants import os
from fileio.utils import dirCheck, fileCheck, fns, join
from spectrum import Spectrum


def text_load( path, filename ):
    if not fileCheck( path, filename ):
        raise IOError( message="text_load: File not found\npath: %s\nfilename: %s" % ( path, filename ), filename=filename )

    with open( join( path, filename ), 'r' ) as infile:
        """ Read header.

        File format:
            namestring=55555-4444-333,z=float(),gmag=float()
            wavelength,flux density,error

        Parse the first line, use the second as CSV reader input
         """
        header = infile.readline().strip().split( ',' )
        namestring = fns( header[ 0 ] )
        z = float( header[ 1 ].strip( "z=" ) )
        gmag = float( header[ 2 ].strip( "gmag=" ) )

        reader = DictReader( infile, fieldnames=infile.readline().strip().split( ',' ) )
        wls = []
        flux = []
        err = []
        for row in reader:
            try:
                wls.append( int( row[ 'wavelength'] ) )
            except ValueError:
                wls.append( float( row[ 'wavelength' ] ) )
            flux.append( float( row[ 'flux density' ] ) )
            err.append( float( row[ 'error' ] ) )
    spec = Spectrum( namestring = namestring, z = z, gmag = gmag )
    spec.setDict( wls, flux, err )
    return spec

def text_write( spec, path, filename ):
    """
    Writes an ASCII formatted spec file with appropriate header information.

    Format can be read in by spec_load_write.text_load() method


    :param spec: spectrum to be written
    :param path: /path/to/write/
    :param filename: filename to write in path
    :type spec: Spectrum
    :type path: str
    :type filename: str
    :return: None
    :rtype: None
    """
    dirCheck( path )

    with open( join( path, filename ), 'w' ) as outfile:
        header = "namestring=%s,z=%f,gmag=%f%s" % ( spec.getNS(), spec.getRS(), spec.getGmag(), os.linesep )
        outfile.writelines( [ header, "wavelength,flux density,error%s" % os.linesep ])

        fieldnames = [ "wavelength", "flux density", "error"]
        writer = DictWriter( outfile, fieldnames= fieldnames)
        writer.writeheader()
        writer.writerows( spec.lineDictList() )

def write( spec, path, filename ):
    """
    Writes a serialized spectrum file at /path/filename
    :param spec: spectrum to the written
    :param path: /path/to/filename
    :param filename: file name to be written to
    :type spec: Spectrum
    :type path: str
    :type filename: str
    :return: None
    """
    dirCheck( path )
    with open( join( path, filename ), 'wb' ) as outfile:
        pickle.dump( spec, outfile, protocol=pickle.HIGHEST_PROTOCOL )

def load( path, filename ):
    """
    Loads the serialized spectrum file at /path/filename

    :param path: /path/to/filename
    :param filename:  file name of spectrum to load
    :type path: str
    :type filename: str
    :rtype: Spectrum
    """
    fileCheck( path, filename )
    return pickle.load( open( join( path, filename ), 'rb' ) )