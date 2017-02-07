import Gnuplot

# TODO: make 4x4 two spectrum multiplot method

def make_points_plotitem( x_data, y_data, error_data = None, title = "", point_type = 7, point_size = 1, color = None ):
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

def make_line_plotitem( x_data, y_data, title = "", with_ = "lines", color = None ):
    if color is not None:
        with_ = f"{with_} lc \"{color}\""

    return Gnuplot.Data( x_data, y_data, title = title, with_ = with_ )

def make_spectrum_plotitem( spec, color = None ):
    _with = "lines"
    if color is not None:
        _with = f'{_with} lc {color}'
    return make_line_plotitem( spec.getWavelengths(), spec.getFluxlist(), title = spec.getNS(), with_= _with )

def ab_z_plot( *plotItems, outpath = None, outfile = None, plotTitle = None, debug = False, **kwargs ):
    from fileio.utils import join

    terminal = 'pdf'
    if "terminal" in kwargs:
        terminal = kwargs[ 'terminal' ]


    g = Gnuplot.Gnuplot( )
    if plotTitle is not None:
        g.title( plotTitle )

    g.xlabel( "Redshift" )
    g.ylabel( "AB Magnitude" )
    g( 'set grid' )
    g( "set key bottom right opaque box")

    if not debug:
        g( f'set terminal {terminal} enhanced color size 9,6')
        output = ""
        for char in join( outpath, outfile ):
            if char == "\\":
                char = r"\\"
            output += char
        g( f'set output "{ output }"')

    g.plot( *plotItems )
    if debug: return g
    g.close()
