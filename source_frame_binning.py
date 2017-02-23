"""
TODO:

    Consider a spectrum in rest frame, binned in 1 A spacing.
    If it were shifted into its original source frame, what would that new spacing be?

    WL 2 * ( 1 + z ) - WL 1 * ( 1 + z ) = ( 1 + z ) * ( WL 2 - WL 1 ) = new_step

    Figure out what the lowest WL would be in rest frame.  Set that as the starting WL in bin process
"""
from typing import Union

from numpy import mean, std

from catalog import shenCat
from fileio.spec_load_write import sspecLoader, text_write
from spectrum import Spectrum


def source_frame_step( spec: Union[ Spectrum, str ], desired_step: float = 1 ) -> float:
    """
    Determines the step size necessary in the spectrum's source frame that will yield the desired_step
    when the spectrum is shifted back to rest.

    :param spec:
    :param desired_step:
    :return:
    """
    if type( spec ) == Spectrum:
        spec = spec.getNS( )
    z = shenCat.subkey( spec, 'z' )
    return (1 + z) * desired_step


def init_source_wl( spec: Spectrum ) -> float:
    source_step = source_frame_step( spec )
    z = shenCat.subkey( spec.getNS( ), 'z' )
    first_wl = spec.getWavelengths( )[ 0 ] / (1 + z)
    first_wl = int( first_wl )
    first_wl *= (1 + z)
    return first_wl


def source_bin( spec: Spectrum, step: float = 1, init_wl: float = None ) -> Spectrum:
    oldwls = spec.getWavelengths( )
    if init_wl is None:
        init_wl = oldwls[ 0 ]

    max_wl = oldwls[ -1 ]

    newwls = [ init_wl ]

    flxlist = [ ]
    errlist = [ ]
    newi = 0
    oldi = 0

    neww = newwls[ newi ]
    oldw = oldwls[ oldi ]
    while neww + step < max_wl:  # Run until the last wavelength in spec is binned
        flux = [ ]  # clear the current range of flux values
        while oldw < neww + step:  # while the old wl is in the current bin, get its flux and advance to the next
            flux.append( spec.getFlux( oldw ) )
            oldi += 1
            oldw = oldwls[ oldi ]

        # see if the flux has more than one value (if so, take the mean and set the err as std deviation)
        # otherwise, assign it that value and error
        if len( flux ) > 1:
            err = std( flux )
            flux = float( mean( flux ) )
        elif len( flux ) == 1:
            err = spec.getErr( oldwls[ oldi - 1 ] )
            flux = flux[ 0 ]

        # if there were no values in this bin range (i.e. the flux variable is still a list, albiet an empty one)
        # then something's wrong.
        if type( flux ) == float:
            flxlist.append( flux )
            errlist.append( err )
            while neww + step < oldw:
                neww += step
            newwls.append( neww )
        else:
            print( "Well, this is awkward.  You're probably caught in an infinte loop." )
            print( f"New WL:{new}, Last old wl:{oldw} on spectrun:{spec.getNS()}" )

    newwls = newwls[ : -1 ]
    spec = spec.cpy_info( )
    spec.setDict( newwls, flxlist, errlist )

    return spec


def binned_source_to_rest( spec: Spectrum, z: float = None ) -> Spectrum:
    """
    Takes in a binned source spectrum and shifts it to rest frame.

    WARNING:  Assumes desired wavelengths will be integer values and called (int) on them as a result

    :param spec: Binned source spectrum
    :param z: Original redshift.  If not passed, it will call spec.getRS() and use that value.
    :type spec: Spectrum
    :type z: float
    :return: Rest frame spectrum
    :rtype: Spectrum
    """
    z = z or spec.getRS( )
    wls = spec.getWavelengths( )
    n = len( wls )
    for wl in wls:
        spec[ int( wl / (1 + z) ) ] = spec[ wl ]
        del spec[ wl ]
    return spec


def main( ):
    outpath = "/home/christopher/Desktop"
    shenCat.load( )
    names = shenCat.keys( )

    test_name = names[ 0 ]
    spec = sspecLoader( test_name )
    text_write( spec, outpath, f"{spec.getNS()}._spec" )

    step = source_frame_step( spec )
    init_wl = init_source_wl( spec )

    spec = source_bin( spec, step, init_wl )
    text_write( spec, outpath, f"{spec.getNS()}.s_spec" )

    spec = binned_source_to_rest( spec )
    text_write( spec, outpath, f"{spec.getNS()}.r_spec" )


if __name__ == '__main__':
    main( )
