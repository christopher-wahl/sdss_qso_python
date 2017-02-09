from typing import List, Union

import Gnuplot

from analysis.pipeline import results_pipeline
from spectrum import Spectrum

def __fix_outpath( path : str, filename : str = None ) -> str:
    from fileio.utils import join
    path = join( path, filename ) if filename is not None else path
    return '"' + ''.join( [ r"\\" if char == "\\" else char for char in path ] ) + '"'

def make_points_plotitem( x_data : list, y_data : list, error_data : list = None, title : str = "", point_type : int = 7, point_size : int = 1, color : str = None ) -> Gnuplot.Data:
    with_ = ""
    if error_data is not None:
        with_ = "yerrorbars"

    with_ = f"{with_} pt {point_type} ps {point_size}"

    if color is not None:
        with_ = f"{with_} lc\"{color}\""

    if error_data is not None:
        from numpy import array
        return Gnuplot.Data( array( [ *zip( x_data, y_data, error_data ) ] ), title=title, with_=with_ )

    return Gnuplot.Data( x_data, y_data, title = title, with_ = with_ )

def make_line_plotitem( x_data : list, y_data : list, title : str = "", with_ : str = "lines", color : str = None ) -> Gnuplot.Data:
    if color is not None:
        with_ = f"{with_} lc \"{color}\""

    return Gnuplot.Data( x_data, y_data, title = title, with_ = with_ )

def make_spectrum_plotitem( spec : Spectrum, color : str = None ) -> Gnuplot.Data:
    _with = "lines"
    if color is not None:
        _with = f'{_with} lc "{color}"'
    return make_line_plotitem( spec.getWavelengths(), spec.getFluxlist(), title = spec.getNS(), with_= _with )

def four_by_four_multiplot( prime : Spectrum, *speclist : list, path : str = None, filename : str = None, plotTitle : str = "", debug : bool = False, **kwargs ) -> Gnuplot.Gnuplot:
    from common.constants import ANGSTROM, FLUX_UNITS

    primeData = make_spectrum_plotitem( prime, color = "royalblue" )
    coSpecs = [ make_spectrum_plotitem( spec, color = "black" ) for spec in speclist ]

    g = Gnuplot.Gnuplot()
    g( 'set grid' )
    g( 'set key opaque box' )
    g.xlabel( u'Wavelength %s' % ANGSTROM )
    g.ylabel( u'Flux Density %s' %FLUX_UNITS )
    if not debug:
        g( "set terminal pdf enhanced color size 11, 8.5" )
        g( f"set output {__fix_outpath( path, filename )}")

    for i in range( 0, len( coSpecs ), 4 ):
        g( f'set multiplot layout 2,2 title "{plotTitle}"' )
        for coSpec in coSpecs[ i : i + 4 ]:
            g.plot( primeData, coSpec )
        g( 'unset multiplot' )

    if debug:
        return g
    g( 'set output' )
    g.close()


def ab_z_plot( primary: Union[ str or Spectrum ],
               points: Union[ results_pipeline or dict or List[ str ] or List[ Spectrum ] ], path: str,
               filename: str, plotTitle: str = "", debug: bool = False ) -> Union[ Gnuplot.Gnuplot or None ]:
    from tools.cosmo import magnitude_evolution
    from catalog import shenCat

    if type( primary ) is Spectrum:
        primary = primary.getNS( )

    """ Make Magnitude Evolutiion Data """
    p_z, p_ab, p_ab_err = shenCat.subkey( primary, 'z', 'ab', 'ab_err' )
    prime_upper_plot = make_line_plotitem( *magnitude_evolution( p_ab + p_ab_err, p_z, splitLists=True )[ :2 ],
                                           title="Upper / Lower Bounds of Expected Evolution", color="grey" )
    prime_lower_plot = make_line_plotitem( *magnitude_evolution( p_ab - p_ab_err, p_z, splitLists=True )[ :2 ],
                                           title="", color="grey" )
    prime_plot = make_line_plotitem( *magnitude_evolution( p_ab, p_z, splitLists=True )[ :2 ],
                                     title="Expected Evolution", color="black" )
    prime_point = make_points_plotitem( [ p_z ], [ p_ab ], error_data=[ p_ab_err ], title=f"{primary}",
                                        color="dark-red" )

    """ Make AB vs Z points data """
    z_data = [ ]
    ab_data = [ ]
    ab_err = [ ]
    if type( points ) is list:
        if type( points[ 0 ] ) is str:
            for ns in points:
                z_data.append( shenCat.subkey( ns, 'z' ) )
                ab_data.append( shenCat.subkey( ns, 'ab' ) )
                ab_err.append( shenCat.subkey( ns, 'ab_err' ) )
        else:
            for spec in points:
                z_data.append( shenCat.subkey( spec.getNS( ), 'z' ) )
                ab_data.append( shenCat.subkey( spec.getNS( ), 'ab' ) )
                ab_err.append( shenCat.subkey( spec.getNS( ), 'ab_err' ) )
    elif type( points ) is dict:
        for ns in points:
            z_data.append( shenCat.subkey( ns, 'z' ) )
            ab_data.append( shenCat.subkey( ns, 'ab' ) )
            ab_err.append( shenCat.subkey( ns, 'ab_err' ) )
    elif isinstance( points, results_pipeline ):
        for ns in points.get_results( ):
            z_data.append( shenCat.subkey( ns, 'z' ) )
            ab_data.append( shenCat.subkey( ns, 'ab' ) )
            ab_err.append( shenCat.subkey( ns, 'ab_err' ) )

    plot_points = make_points_plotitem( z_data, ab_data, ab_err, color="royalblue" )

    """ Data has been formed.  Make actual plot """
    g = Gnuplot.Gnuplot( debug=1 if debug else 0 )
    g.title( plotTitle )
    g.xlabel( "Redshift" )
    g.ylabel( "AB Magnitude" )
    g( "set key bottom right opaque box" )
    g( "set grid" )

    if not debug:
        from fileio.utils import dirCheck, join
        dirCheck( path )
        g( 'set terminal pdf enhanced size 9,6' )
        g( f'set output {__fix_outpath( path, filename ) }' )

    g.plot( plot_points, prime_plot, prime_upper_plot, prime_lower_plot, prime_point )

    if not debug:
        g( 'set output' )
        g.close( )
        return None
    return g
