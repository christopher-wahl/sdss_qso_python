import Gnuplot

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

def ab_z_plot( *plotItems, path : str = None, filename : str = None, plotTitle : str = None, debug : bool = False, **kwargs ) -> Gnuplot.Gnuplot:
    from fileio.utils import dirCheck

    terminal = 'pdf'
    if "terminal" in kwargs:
        terminal = kwargs[ 'terminal' ]


    g = Gnuplot.Gnuplot()
    if plotTitle is not None:
        g.title( plotTitle )

    g.xlabel( "Redshift" )
    g.ylabel( "AB Magnitude" )
    g( 'set grid' )
    g( "set key bottom right opaque box")

    if not debug:
        dirCheck( path )
        g( f'set terminal {terminal} enhanced color size 9,6')
        g( f'set output { __fix_outpath( path, filename ) }')

    g.plot( *plotItems )
    if debug: return g
    g.close()

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