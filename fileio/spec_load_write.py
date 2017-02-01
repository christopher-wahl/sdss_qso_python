from csv import DictReader

from fileio.utils import fileCheck, fns, join
from spectra import spectrum


def text_load( path, filename ):
    if not fileCheck( path, filename ):
        raise IOError( "text_load: File not found\npath: %s\nfilename: %s" % ( path, filename ) )

    with open( join( path, filename ), 'r' ) as infile:
        """ Read header.

        File format:
            namestring=55555-4444-333,z=float(),gmag=float()
            wavelength,flux density,error

        Parse the first line, use the second as CSV reader input
         """
        header = infile.readline( 1 ).strip().split( ',' )
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
    spec = spectrum( namestring = namestring, z = z, gmag = gmag )
    spec.setDict( wls, flux, err )
    return spec