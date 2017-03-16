from catalog import shenCat
from common.constants import MGII_RANGE, OIII_RANGE
from fileio.spec_load_write import async_rspec

shenCat.load( )

speclist = async_rspec( shenCat.keys( ) )
for spec in speclist:
    spec.trim( wlLow=MGII_RANGE[ 0 ], wlHigh=OIII_RANGE[ 1 ] )
    i = 0
    max_i = 0
    wls = spec.getWavelengths( )
    for wl in wls:
        if spec.getErr( wl ) == 0:
            i += 1
        else:
            max_i = max( max_i, i )
            i = 0

    if max_i > 100:
        del shenCat[ spec.getNS( ) ]
        print( spec.getNS( ) )

print( len( shenCat ) )
# shenCat.rewrite()
shenCat.export_text( )
