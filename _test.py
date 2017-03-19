from numpy import log10
from scipy.optimize import curve_fit

from catalog import shenCat
from common.constants import BASE_PROCESSED_PATH
from fileio.list_dict_utils import namestring_dict_reader
from fileio.utils import fns, getFiles, join
from tools.plot import ab_z_plot

FITTING_FUNC = log10


def fit_func( x, a, b ):
    return a * FITTING_FUNC( x ) + b


def fit_log( data_dict: dict ):
    datax, datay = [ ], [ ]
    for dp in data_dict:
        datax.append( shenCat.subkey( dp, 'z' ) )
        datay.append( shenCat.subkey( dp, 'ab' ) )
    coeff, pcov = curve_fit( fit_func, datax, datay )
    return coeff[ 0 ], coeff[ 1 ]


basepath = join( BASE_PROCESSED_PATH, "Analysis/EM 15 CONT 100 Old" )
ipath = join( basepath, "Individual Results" )
plotpath = join( basepath, "Plot" )
files = getFiles( ipath, ".csv" )
countd = [ ]
for f in files:
    countd.append( (fns( f ), sum( [ 1 for line in open( join( ipath, f ), 'r' ) ] )) )

countd.sort( key=lambda x: x[ 1 ] )

for c in countd:
    ns, count = c
    if 20 < count < 50:
        indict = namestring_dict_reader( ipath, f"{ns}.csv" )
        a, b = fit_log( indict )
        if 4.5 < a < 5.5:
            print( f"{ns} : {a} log10( x ) + {b}" )
            ab_z_plot( plotpath, f"{ns}.png", ns, indict, rs_fit_func=lambda z: fit_func( z, a, b ),
                       rs_fit_title=f"{a} log10 + {b}", png=True )
