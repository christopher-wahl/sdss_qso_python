from spectrum import Spectrum

DEF_ERR_DICT = { 0x40000: 'SP_MASK_FULLREJECT',  # Pixel fully rejected in extraction                   18      2.621e5
                 0x800000: 'SP_MASK_BRIGHTSKY',  # Sky level > flux + 10*(flux error)                   23      8.389e6
                 0x1000000: 'SP_MASK_NODATA' }  # No data available in combine B-spline                24      1.678e7


def fit_spec_loader( path: str, filename: str, error_dict: dict = DEF_ERR_DICT ) -> Spectrum:
    """
    Loads a FIT spectrum file from SDSS DR 7 or lower.  Converts it into Spectrum type.

    Note: error_dict has the actual mask values as keys.  Loader will iterate through these keys
    and delete any points where these keys are found.  The dict format is an artifact where the values attached
    to each key are the SDSS error names in text.

    :param path: /path/to/file
    :param filename: filename.fits
    :param error_dict: Defaults to DEF_ERR_DICT defined in this file if not passed
    :type path: str
    :type filename: str
    :type error_dict: dict
    :rtype: Spectrum
    """
    from astropy.io.fits import getheader, getdata
    from fileio.utils import fileCheck, join
    from catalog import shenCat

    fileCheck( path, filename )

    shenCat.load( )
    infile = join( path, filename )

    # Assemble basic info from the header
    # Check if the HW redshift is included in the shenCat.  If so, assign it,
    # otherwise use the one in the file
    header = getheader( infile, 0 )
    namestring = "%05i-%04i-%03i" % (header[ 'MJD' ], header[ 'PLATEID' ], header[ 'FIBERID' ])
    z = shenCat.subkey( namestring, 'z' ) if namestring in shenCat else float( header[ 'z' ] )
    gmag = float( header[ 'MAG' ].split( )[ 1 ] )  # Stored as UGRIZ

    data = getdata( infile, 0 )
    flux_data = data[ 0 ].tolist( )  # first apertrure is the calibrated spectrum flux density
    # data[ 1 ] is the continuum-subtracted spectrum.  Not of interest
    err_data = data[ 2 ].tolist( )  # third is the +/- of flux denisty
    mask_data = data[ 3 ].tolist( )  # error mask

    # Wavelengths are packed around a central region at binned intervals
    # So the FIT file only stores the log of the first WL, the number of pixels
    # from the first WL and the log of bin spacing.  Need to unpack
    # these values to turn them into wavelengths in Angstroms
    c0 = header[ 'coeff0' ]
    c1 = header[ 'coeff1' ]
    num_pixels = header[ 'naxis1' ]
    # Unpacking happens here
    wavelengths = [ pow( 10, c0 + c1 * n ) for n in num_pixels ]

    out_spec = Spectrum( namestring=namestring, z=z, gmag=gmag )
    out_spec.setDict( wavelengths, flux_data, err_data )

    # Mask out the errors
    for i in range( len( err_data ) ):
        if __bit_mask( err_data[ i ], error_dict ):
            del out_spec[ wavelengths[ i ] ]
    return out_spec


def __bit_mask( mask: int, mask_dict: dict ) -> bool:
    for m in mask_dict:
        if int( mask ) & m: return True
    return False