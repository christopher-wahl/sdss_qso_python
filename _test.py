from analysis.divide import divide
from catalog import shenCat
from fileio.spec_load_write import rspecLoader

s0 = rspecLoader( shenCat.keys()[ 0 ] )
s1 = rspecLoader( shenCat.keys()[ 1 ] )

d = divide( s0, s1 )

from analysis.slope_fit import spectrum_linear_fit

m, b = spectrum_linear_fit( d )
print( f"y = {m} x + {b}" )
