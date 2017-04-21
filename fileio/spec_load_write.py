import pickle
from csv import DictReader, DictWriter
from typing import List, Union

from common.constants import BINNED_SPEC_PATH, REST_SPEC_PATH, SOURCE_SPEC_PATH, os
from fileio.utils import dirCheck, extCheck, fileCheck, fns, join, ns2f
from spectrum import Iterable, Spectrum

"""
The methods contained here exist for the sole purpose of reading and writing Spectrum class files to/from the disk.
Unless specified by the "text_" delineation in the method name, all methods write/load serialized objects using
Python's pickle package.  All are written with the highest protocol.

"async_" delineated methods make use of Python's asyncio package and common.async_tool's generic_async_wrapper method
"""
def text_load( path: str, filename: str ) -> Spectrum:
    """
    Loads the standardized ASCII format Spectrum file as written by text_write.
    
    Note: If for some reason, the redshift and/or gmag values cannot be converted to a float,
    they will be assigned a value of -1
    
    :param path: /path/to/input file
    :param filename: input file name
    :type path: str
    :type filename: str
    :return: Loaded Spectrum
    :rtype: Spectrum
    :raises: FileNotFoundError
    """
    fileCheck( path, filename )

    with open( join( path, filename ), 'r' ) as infile:
        """ Read header.

        File format:
            namestring=55555-4444-333,z=float(),gmag=float()
            wavelength,flux density,error

        Parse the first line, use the second as CSV reader input
         """
        header = infile.readline( ).strip( ).split( ',' )
        namestring = fns( header[ 0 ] )
        try:
            z = float( header[ 1 ].strip( "z=" ) )
        except ValueError:
            z = -1
        try:
            gmag = float( header[ 2 ].strip( "gmag=" ) )
        except ValueError:
            gmag = -1

        reader = DictReader( infile, fieldnames=infile.readline( ).strip( ).split( ',' ) )
        wls = [ ]
        flux = [ ]
        err = [ ]
        for row in reader:
            try:
                wls.append( int( row[ 'wavelength' ] ) )
            except ValueError:
                wls.append( float( row[ 'wavelength' ] ) )
            flux.append( float( row[ 'flux density' ] ) )
            err.append( float( row[ 'error' ] ) )
    spec = Spectrum( namestring=namestring, z=z, gmag=gmag )
    spec.setDict( wls, flux, err )
    return spec


def text_write( spec: Spectrum, path: str, filename: str ) -> None:
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
        header = "namestring=%s,z=%f,gmag=%f%s" % (spec.getNS( ), spec.getRS( ), spec.getGmag( ), os.linesep)
        outfile.writelines( header )

        fieldnames = [ "wavelength", "flux density", "error" ]
        writer = DictWriter( outfile, fieldnames=fieldnames )
        writer.writeheader( )
        writer.writerows( spec.lineDictList( ) )


def load( path: str, filename: str ) -> Spectrum:
    """
    Loads the serialized spectrum file at /path/filename

    :param path: /path/to/filename
    :param filename:  file name of spectrum to load
    :type path: str
    :type filename: str
    :rtype: Spectrum
    :raises: FileNotFoundError
    """
    fileCheck( path, filename )
    return pickle.load( open( join( path, filename ), 'rb' ) )


def write( spec: Spectrum, path: str, filename: str ) -> None:
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


def bspecLoader( namestring: str ) -> Spectrum:
    """
    Loads a single Spectrum from BINNED_SPEC_PATH
    
    :param namestring: Namestring of desired spectrum
    :type namestring: str
    :rtype: Spectrum
    """
    return load( BINNED_SPEC_PATH, ns2f( namestring, ".bspec" ) )


def rspecLoader( namestring: str ) -> Spectrum:
    """
    Loads a single Spectrum from REST_SPEC_PATH

    :param namestring: Namestring of desired spectrum
    :type namestring: str
    :rtype: Spectrum
    """
    return load( REST_SPEC_PATH, ns2f( namestring, ".rspec" ) )


def sspecLoader( namestring: str ) -> Spectrum:
    """
    Loads a single Spectrum from SOURCE_SPEC_PATH

    :param namestring: Namestring of desired spectrum
    :type namestring: str
    :rtype: Spectrum
    """
    return load( SOURCE_SPEC_PATH, ns2f( namestring, ".spec" ) )


def async_bspec( namelist: List[ str ] ) -> List[ Spectrum ]:
    """
    Loads all given binned, observed frame spectra from the BINNED_SPEC_PATH using async_load

    :param namelist:  Iterable
    :type namelist: Iterable[ str ]
    :return: List of binned, observed frame spectra
    :rtype: List[ Spectrum ]
    """
    return async_load( BINNED_SPEC_PATH, namelist, ".bspec" )


def async_rspec( namelist: Iterable[ str ] ) -> List[ Spectrum ]:
    """
    Loads all given rest frame spectra from the REST_SPEC_PATH using async_load
    
    :param namelist:  Iterable
    :type namelist: Iterable[ str ]
    :return: List of rest frame spectra
    :rtype: List[ Spectrum ]
    """
    return async_load( REST_SPEC_PATH, namelist, ".rspec" )


def async_load( path: str, filelist: List[ str ], extention: str = None ) -> List[ Spectrum ]:
    """
    Uses asyncio to load serialized Spectrum from filelist ( list in [ str() ] form )

    If extension is specified, each filename in filelist will be concactated with it.  Elsewise, ignored.

    :param path: /path/to/directory
    :param filelist: filenames of spectra to be loaded
    :param extention: (optional) file extention to append to each filename before loading
    :type path: str
    :type filelist: list
    :type extention: str
    :return: list of loaded Spectrum type
    :rtype: list
    """
    from tools.async_tools import generic_async_wrapper
    import asyncio

    async def __async_load_wrapper( path, filename ):
        return load( path, filename )

    output_list = [ ]
    load_loop = asyncio.new_event_loop( )

    if extention is not None:
        filelist = [ f + extCheck( extention ) for f in filelist ]

    try:
        load_loop.run_until_complete(
                generic_async_wrapper( [ (path, filename) for filename in filelist ], __async_load_wrapper,
                                       output_list ) )
    finally:
        load_loop.close( )

    return output_list


def async_write( path: str, speclist: List[ Spectrum ], extention: str = ".spec" ) -> None:
    """
    Uses asyncio to write a list of Spectrum to the disk.

    Will set filename from spectrum namestring.  If extention is not specificed, will default to ".spec"

    :param path: /path/to/directory
    :param speclist: list of spectrum to output
    :param extention: desired file extention
    :type path: str
    :type speclist: list
    :type extention: str
    :rtype: None
    """
    from tools.async_tools import generic_async_wrapper
    import asyncio

    async def __async_write_wrapper( path, spectrum, extention ):
        write( spectrum, path, ns2f( spectrum.getNS( ), extention ) )

    write_loop = asyncio.new_event_loop( )

    try:
        write_loop.run_until_complete(
                generic_async_wrapper( [ (path, spec, extention) for spec in speclist ], __async_write_wrapper ) )
    finally:
        write_loop.close( )


def async_rspec_scaled( namelist: Iterable[ str ], scale_to: Union[ float, Spectrum ] ) -> List[ Spectrum ]:
    """
    Uses the asyncio library to load the given namelist of Spectrum namestrings from the default rest frame spectra
    folder REST_SPEC_PATH.  While spectra are loaded from the disk, they are scaled to the given value for the scale_to variable
    centered on the DEFAULT_SCALE_WL constant in common.constants.
    
    scale_to can be either a floating point value (which is passed to the Spectrum.scale() method) or a Spectrum class,
    in which case the average flux density around the DEF_SCALE_WL constant will be determined and passed.
    
    :param namelist: List of MJD-PLATE-FIBER namestrings.  The corresponding MJD-PLATE-FIBER.rspec must be present
     in the REST_SPEC_PATH.
    :param scale_to: float or Spectrum class which all loaded spectra will be scaled to.
    :type namelist: Iterable
    :type scale_to: Spectrum or float
    :return: Scaled restframe speclist
    :rtype: List[ Spectrum ]
    """
    from tools.async_tools import generic_async_wrapper
    from common.constants import REST_SPEC_PATH
    import asyncio

    if type( scale_to ) is Spectrum:
        scale_to = scale_to.aveFlux( )

    async def __async_scaled_load_wrapper( path, filename, scaleflx ):
        return load( path, filename ).scale( scaleflux=scaleflx )

    output_list = [ ]
    load_loop = asyncio.new_event_loop( )

    try:
        load_loop.run_until_complete(
                generic_async_wrapper( [ (REST_SPEC_PATH, f"{ns}.rspec", scale_to) for ns in namelist ],
                                       __async_scaled_load_wrapper,
                                       output_list ) )
    finally:
        load_loop.close( )

    return output_list
