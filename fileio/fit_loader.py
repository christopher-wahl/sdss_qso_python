from spectrum import Spectrum

# The standard mask values
DEF_MASK_DICT = { 0x40000: 'SP_MASK_FULLREJECT',  # Pixel fully rejected in extraction                   18      2.621e5
                 0x800000: 'SP_MASK_BRIGHTSKY',  # Sky level > flux + 10*(flux error)                   23      8.389e6
                 0x1000000: 'SP_MASK_NODATA' }  # No data available in combine B-spline                24      1.678e7

# These codes are for reference
allMaskCodes = { 0x000: 'SP_MASK_OK',  # No issues detected                                             -inf    x
                 0x001: 'SP_MASK_NOPLUG',  # Fiber not listed in plugmap file                           0       1e0
                 0x002: 'SP_MASK_BADTRACE',  # Bad trace from routine TRACE320CRUDE                     1       2e0
                 0x004: 'SP_MASK_BADFLAT',  # Low counts in fiberflat                                   2       4e0
                 0x008: 'SP_MASK_BADARC',  # Bad arc solution                                           3       8e0
                 0x010: 'SP_MASK_MANYBADCOL',  # More than 10% pixels are bad columns                   4       1.6e1
                 0x020: 'SP_MASK_MANYREJECT',  # More than 10% pixels are rejected in extraction        5       3.2e1
                 0x040: 'SP_MASK_LARGESHIFT',  # Large spatial shift between flat & object position     6       6.4e1
                 0x10000: 'SP_MASK_NEARBADPIX',  # Bad pixel within 3 pixels of trace                   16      6.554e4
                 0x20000: 'SP_MASK_LOWFLAT',  # Flat field less than 0.5                                17      1.331e5
                 0x40000: 'SP_MASK_FULLREJECT',  # Pixel fully rejected in extraction                   18      2.621e5
                 0x80000: 'SP_MASK_PARTIALREJ',  # Some pixels rejected in extraction                   19      5.243e5
                 0x100000: 'SP_MASK_SCATLIGHT',  # Scattered light significant                          20      1.049e6
                 0x200000: 'SP_MASK_CROSSTALK',  # Cross-talk significant                               21      2.097e6
                 0x400000: 'SP_MASK_NOSKY',  # Sky level unknown at this wavelength                     22      4.194e6
                 0x800000: 'SP_MASK_BRIGHTSKY',  # Sky level > flux + 10*(flux error)                   23      8.389e6
                 0x1000000: 'SP_MASK_NODATA',  # No data available in combine B-spline                  24      1.678e7
                 0x2000000: 'SP_MASK_COMBINEREJ',  # Rejected in combine B-spline                       25      3.355e7
                 0x4000000: 'SP_MASK_BADFLUXFACTOR',  # Low flux-calibration or flux-correction factor  26      6.711e7
                 0x8000000: 'SP_MASK_BADSKYCHI',  # Chi^2 > 4 in sky residuals at this wavelength       27      1.342e8
                 0x10000000: 'SP_MASK_REDMONSTER',  # Contiguous region of bad chi^2 in sky residuals   28      2.684e8
                 0x40000000: 'SP_MASK_EMLINE' }  # Emission line detected here                          30      1.074e9

def fit_spec_loader( path: str, filename: str, mask_dict: dict = DEF_MASK_DICT ) -> Spectrum:
    """
    Loads a FIT spectrum file from SDSS DR 7 or lower.  Converts it into Spectrum type.

    Note: error_dict has the actual mask values as keys.  Loader will iterate through these keys
    and delete any points where these keys are found.  The dict format is an artifact where the values attached
    to each key are the SDSS error names in text.

    :param path: /path/to/file
    :param filename: filename.fits
    :param mask_dict: Defaults to DEF_ERR_DICT defined in this file if not passed
    :type path: str
    :type filename: str
    :type mask_dict: dict
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

    # Wavelength values are not stored in FIT files.  Only three values are available, and these are used to
    # generate the wavelengths which correspond to the pixels
    #   i.e. wl[ pixel 0 ] -> flux density[ 0 ], error[ 0 ], mask[ 0 ], etc
    #
    # Those 3 values are:
    #   naxis1 : number of pixels stored
    #   coeff0 : Log10 of the first wavelength
    #   coeff1 : Log10 of the dispersion coefficient
    #
    # Log10( wavelengths ) are generated by the function:   log_wl_n( n ) = c0 + c1 * n
    # where n is the nth pixel
    # Then the wavelength, in angstroms is given 10^(log_wl_n)
    c0 = header[ 'coeff0' ]
    c1 = header[ 'coeff1' ]
    num_pixels = header[ 'naxis1' ]
    # The actual wavelength generation happens here
    wavelengths = [ pow( 10, c0 + c1 * n ) for n in num_pixels ]

    out_spec = Spectrum( namestring=namestring, z=z, gmag=gmag )
    out_spec.setDict( wavelengths, flux_data, err_data )

    # Mask out the errors
    for i in range( len( err_data ) ):
        if __bit_mask( mask_data[ i ], mask_dict ):
            del out_spec[ wavelengths[ i ] ]
    return out_spec


def __bit_mask( mask: int, mask_dict: dict ) -> bool:
    for m in mask_dict:
        if int( mask ) & m: return True
    return False
