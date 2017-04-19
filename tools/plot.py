from typing import Callable, List, Union

import Gnuplot

from analysis.pipeline import results_pipeline
from spectrum import Iterable, Spectrum


def __fix_outpath( path: str, filename: str = None ) -> str:
    from fileio.utils import join
    path = join( path, filename ) if filename is not None else path
    return '"' + ''.join( [ r"\\" if char == "\\" else char for char in path ] ) + '"'


def make_points_plotitem( x_data: Iterable, y_data: Iterable, error_data: Iterable = None, title: str = "",
                          point_type: int = 7, point_size: int = 1, color: str = None ) -> Gnuplot.Data:
    with_ = ""
    if error_data is not None:
        with_ = "yerrorbars"

    with_ = f"{with_} points pt {point_type} ps {point_size}"

    if color is not None:
        with_ = f"{with_} lc \"{color}\""

    if error_data is not None:
        from numpy import array
        return Gnuplot.Data( array( [ *zip( x_data, y_data, error_data ) ] ), with_=with_, title=title )

    return Gnuplot.Data( x_data, y_data, title=title, with_=with_ )


def make_line_plotitem( x_data: Iterable, y_data: Iterable, title: str = "", with_: str = "",
                        color: str = None ) -> Gnuplot.Data:
    """
    Takes two iterables of x and y data (order paired) and returns a line plot object in Gnuplot.Data format. 
    
    :param x_data: 
    :type x_data: Iterable
    :param y_data: 
    :type y_data: Iterable
    :param title:  Plot object title - what will be displayed in the key
    :type title: str
    :param with_: Customizable "with ..." string.  Will be concatenated with "... lc 'color'" if a color is passed.
    :type with_: str
    :param color: Gnuplot compatible color for the plot item.
    :type color: str
    :return: Gnuplot plotable data
    :rtype: Gnuplot.Data
    """
    with_ = "lines " + with_
    if color is not None:
        with_ = f"{with_} lc \"{color}\""

    return Gnuplot.Data( x_data, y_data, title=title, with_=with_ )


def make_spectrum_plotitem( spec: Spectrum, color: str = None ) -> Gnuplot.Data:
    """
    Takes in a Spectrum class and returns Gnuplot.Data format for plotting using the data within the Spectrum object
     
    :param spec:
    :type spec: Spectrum
    :param color: 
    :type color: str
    :return: 
    :rtype: Gnuplot.Data
    """
    _with = "lines"
    if color is not None:
        _with = f'{_with} lc "{color}"'
    return make_line_plotitem( spec.getWavelengths(), spec.getFluxlist(), title=spec.getNS(), with_=_with )


def four_by_four_multiplot( prime: Spectrum, speclist: list, path: str = None, filename: str = None,
                            plotTitle: str = "", debug: bool = False ) -> Union[ Gnuplot.Gnuplot, None ]:
    from common.constants import ANGSTROM, FLUX_UNITS

    primeData = make_spectrum_plotitem( prime, color="royalblue" )
    coSpecs = [ make_spectrum_plotitem( spec, color="black" ) for spec in speclist ]

    g = Gnuplot.Gnuplot()
    g( 'set grid' )
    g( 'set key opaque box' )
    g.xlabel( u'Wavelength %s' % ANGSTROM )
    g.ylabel( u'Flux Density %s' % FLUX_UNITS )
    if not debug:
        g( "set terminal pdf enhanced color size 11, 8.5" )
        g( f"set output {__fix_outpath( path, filename )}" )

    for i in range( 0, len( coSpecs ), 4 ):
        g( f'set multiplot layout 2,2 title "{plotTitle}"' )
        for coSpec in coSpecs[ i: i + 4 ]:
            g.plot( coSpec, primeData )
        g( 'unset multiplot' )

    if debug:
        return g
    g( 'set output' )
    g.close()


def ab_z_plot( path: str, filename: str, primary: Union[ str or Spectrum ],
               points: Union[ results_pipeline or dict or List[ str ] or List[ Spectrum ] ], plotTitle: str = "",
               n_sigma: float = 1, rs_fit_func: Callable[ [ float ], float ] = None, rs_fit_title: str = None,
               png: bool = False,
               debug: bool = False ) -> Union[ Gnuplot.Gnuplot or None ]:
    from tools.cosmo import magnitude_evolution
    from catalog import shenCat

    if primary is not None:
        if type( primary ) is Spectrum:
            if primary.getNS() in shenCat:
                p_z, p_ab, p_ab_err = shenCat.subkey( primary.getNS(), 'z', 'ab', 'ab_err' )
            else:
                p_z, p_ab, p_ab_err = primary.getRS(), primary.magAB(), primary.abErr()
            primary = primary.getNS()
        else:
            p_z, p_ab, p_ab_err = shenCat.subkey( primary, 'z', 'ab', 'ab_err' )

        """ Make Magnitude Evolutiion Data """
        p_ab_err *= n_sigma
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
                ab_err.append( n_sigma * shenCat.subkey( ns, 'ab_err' ) )
        else:
            for spec in points:
                z_data.append( shenCat.subkey( spec.getNS(), 'z' ) )
                ab_data.append( shenCat.subkey( spec.getNS(), 'ab' ) )
                ab_err.append( n_sigma * shenCat.subkey( spec.getNS(), 'ab_err' ) )
    elif type( points ) is dict:
        for ns in points:
            z_data.append( shenCat.subkey( ns, 'z' ) )
            ab_data.append( shenCat.subkey( ns, 'ab' ) )
            ab_err.append( n_sigma * shenCat.subkey( ns, 'ab_err' ) )
    elif isinstance( points, results_pipeline ):
        for ns in points.get_results():
            z_data.append( shenCat.subkey( ns, 'z' ) )
            ab_data.append( shenCat.subkey( ns, 'ab' ) )
            ab_err.append( n_sigma * shenCat.subkey( ns, 'ab_err' ) )

    plot_points = make_points_plotitem( z_data, ab_data, ab_err, color="royalblue" )
    plotlist = [ plot_points ]
    if primary is not None:
        plotlist.extend( [ prime_plot, prime_upper_plot, prime_lower_plot, prime_point ] )
    if rs_fit_func is not None:
        fitx = [ (z / 100) for z in range( 46, 83 ) ]
        fity = [ rs_fit_func( z ) for z in fitx ]
        fitplot = make_line_plotitem( fitx, fity, "Fit Function" if rs_fit_title is None else rs_fit_title,
                                      with_="lines dt '-'", color="grey50" )
        plotlist.append( fitplot )

    """ Data has been formed.  Make actual plot """
    g = Gnuplot.Gnuplot( persist=debug )
    g.title( r"%s" % plotTitle )
    g.xlabel( "Redshift" )
    g.ylabel( "AB Magnitude" )
    g( "set key bottom right opaque box" )
    g( "set grid" )
    g( "set xrange [0.46:0.82]" )

    if not debug:
        from fileio.utils import dirCheck, join
        dirCheck( path )
        if png:
            g( 'set terminal png enhanced size 800, 600' )
        else:
            g( 'set terminal pdf enhanced size 9,6' )
        g( f'set output {__fix_outpath( path, filename ) }' )

    g.plot( *plotlist )

    if not debug:
        g( 'set output' )
        g.close()
        return None
    return g


def spectrum_plot( spec: Spectrum, path: str, filename: str, color: str = "royalblue", debug: bool = False ) -> None:
    """
    Simple spectrum plotter.  Passes values to Gnuplot.py.  Plots in PDF format.
    
    If debug = True, no values will be written to the disk and Gnuplot will be initialized with persist = True and
    the path/filename values should be passed as empty strings "" to avoid an error.
    
    :param spec: Spectrum to be plot
    :type spec: Spectrum
    :param path: /path/to/output/file
    :type path: str
    :param filename: output file name
    :type filename: str
    :param color: Color to make the spectrum line.  Defaults to "royalblue."  Must be a color acceptable to Gnuplot
    :type color: str
    :param debug: Use the debug process, print outputs on the screen
    :type debug: bool
    :rtype: None
    """
    from common.constants import ANGSTROM, FLUX_UNITS
    from fileio.utils import dirCheck

    if not debug: dirCheck( path )
    g = Gnuplot.Gnuplot( persist=debug )
    g.title( spec.getNS() )
    g.xlabel( f"Wavelength ({ANGSTROM})" )
    g.ylabel( f"Flux Density ({FLUX_UNITS})" )
    g( 'set key top right' )
    g( 'set grid' )
    if not debug:
        g( 'set terminal pdf color enhanced size 9,6' )
        if ".pdf" not in filename:
            filename += ".pdf"
        g( f'set output {__fix_outpath( path, "%s" % filename )}' )

    g.plot( make_spectrum_plotitem( spec, color=color ) )

    if not debug:
        g( 'set output' )


def xy_scatterplot( path: str, filename: str, x_data: Iterable, y_data: Iterable, y_error_bars: Iterable = None,
                    dataTitle: str = None, plotTitle: str = None, x_label: str = None, y_label: str = None,
                    plotcolor: str = "royalblue", debug: bool = False ) -> None:
    """
    Simple XY scatterplot production.  Plots using PDF terminal.  If passing debug=True, no file will be written to 
    disk.  To avoid typing errors, it is desirable to pass "" for path and filename variables.
    
    :param path: /path/to/output file
    :type path: str
    :param filename: output file name
    :type filename: str
    :param x_data: 
    :type x_data: Iterable
    :param y_data: 
    :type y_data: Iterable
    :param y_error_bars:
    :type y_error_bars: Iterable
    :param dataTitle: Title of the xy data that will be displayed in the key.  If not passed, key will be removed from the plot.
    :type dataTitle: str
    :param plotTitle: 
    :type plotTitle: str
    :param x_label: X-axis label
    :type x_label: str
    :param y_label: Y-axis label
    :type y_label: str
    :param plotcolor: Color of plot points.  Must be a Gnupot compatible colorname such as "dark-red" 
    :type plotcolor: str
    :param debug: 
    :type debug: bool
    :return: 
    :rtype: None
    """
    from fileio.utils import dirCheck

    if not debug: dirCheck( path )
    g = Gnuplot.Gnuplot( persist=debug )

    if plotTitle is not None: g.title( plotTitle )
    if x_label is not None: g.xlabel( x_label )
    if y_data is not None: g.ylabel( y_label )
    g( 'set grid' )
    if dataTitle is None:
        g( "unset key" )
    if not debug:
        g( 'set terminal pdf color enhanced size 9,6' )
        if ".pdf" not in filename:
            filename += ".pdf"
        g( f'set output {__fix_outpath( path, "%s" % filename )}' )
    g.plot( make_points_plotitem( x_data, y_data, y_error_bars, title=dataTitle, color=plotcolor ) )
    if not debug:
        g( 'set output' )
