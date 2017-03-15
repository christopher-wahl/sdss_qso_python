from catalog import shenCat
from fileio.spec_load_write import async_rspec_scaled, rspecLoader

shenCat.load( )
del shenCat[ '53799-1703-640' ]

shenCat.rewrite( )

exit( )
p = "54115-2493-610"

prime = rspecLoader( "54115-2493-610" )

speclist = async_rspec_scaled( shenCat.keys( ), prime )
print( len( speclist ) )
