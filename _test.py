from catalog import shenCat
from fileio.list_dict_utils import namestring_dict_reader, namestring_dict_writer
from tools.plot import xy_scatterplot

inpath, infile = "/home/christopher/Desktop/103/", "53327-1928-103.csv"
namestring_dict_writer( shenCat, inpath, "shenCat.csv" )
indict = namestring_dict_reader( inpath, infile )
for ns in indict:
    indict[ ns ] = shenCat[ ns ]
namestring_dict_writer( indict, inpath, infile )
exit( 0 )

plotx = [ ]
ploty = [ ]
plotyerr = [ ]
all_x = [ shenCat[ ns ][ 'z' ] for ns in shenCat ]
all_y = [ shenCat[ ns ][ 'ew_hb' ] for ns in shenCat ]

for ns in indict:
    plotx.append( shenCat[ ns ][ 'z' ] )
    ploty.append( shenCat[ ns ][ 'ew_hb' ] )
    plotyerr.append( shenCat[ ns ][ 'ew_hb_err' ] )

xy_scatterplot( "", "", plotx, ploty, plotyerr, debug=True )
xy_scatterplot( "", "", all_x, all_y, debug=True )  # , plotcolor="dark-red" )
