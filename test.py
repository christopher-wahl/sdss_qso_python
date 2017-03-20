from numpy import log10
from scipy.optimize import curve_fit

from catalog import shenCat
from common.constants import BASE_ANALYSIS_PATH, join
from fileio.list_dict_utils import namestring_dict_reader
from fileio.utils import fns, getFiles
from tools.cosmo import magnitude_at_redshift


def fit_func( x, a, b ):
    return a * log10( x ) + b


def fit_log( data_dict: dict ):
    datax, datay = [ ], [ ]
    for dp in data_dict:
        datax.append( shenCat.subkey( dp, 'z' ) )
        datay.append( shenCat.subkey( dp, 'ab' ) )
    coeff, pcov = curve_fit( fit_func, datax, datay )
    return coeff[ 0 ], coeff[ 1 ]


def find_chi( f ):
    ns = fns( f )
    pm0, pz0 = shenCat.subkey( ns, 'ab', 'z' )
    indict = namestring_dict_reader( ipath, f )
    s = 0
    i = 0
    for specns in indict:
        pmag = magnitude_at_redshift( pm0, pz0, shenCat[ specns ][ 'z' ] )
        s += pow( pmag - shenCat[ specns ][ 'ab' ], 2 ) / pmag
        i += 1
    try:
        s /= i
    except ZeroDivisionError:
        pass
    if i < 2:
        return s, i, 0, 0
    return (s, i, *fit_log( indict ))


MG_MAX = 5
basepath = join( BASE_ANALYSIS_PATH, "EM 15 CONT 100 Old" )
sourcepath = join( basepath, "source" )
comppath = join( basepath, "Composites" )
ipath = join( basepath, "Individual Results" )

# spec = "53674-2265-087"; indict = namestring_dict_reader( ipath, f"{spec}.csv" ); ab_z_plot( comppath, f"{spec}.pdf", spec, indict ); exit()

if __name__ == '__main__':
    filelist = sorted( getFiles( ipath, ".csv" ) )
    minchi = [ ]
    for f in filelist:
        minchi.append( (fns( f ), *find_chi( f )) )
    minchi.sort( key=lambda x: abs( 5 - x[ 3 ] ) )
    minchi = filter( lambda x: x[ 2 ] > 20, minchi )

    [ print( *m ) for m in minchi ]
