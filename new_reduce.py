from catalog import shenCat
from fileio.list_dict_utils import namestring_dict_reader, simple_list_reader
from fileio.utils import join
from tools.plot import ab_z_plot


shenCat.load( )

path, filename = "/media/christopher/Research/Processed/Analysis/EM + C Search/EM 20 CONT 200 Old/", "final_count.csv"
countlist = simple_list_reader( path, filename )

plotpath = join( path, "Plots2" )
indipath = join( path, "Individual Results" )
for line in countlist:
    if 15 > line[ 1 ] > 5:
        rdict = namestring_dict_reader( indipath, f"{line[ 0 ]}.csv" )
        ab_z_plot( plotpath, f"{line[ 0 ]}.pdf", line[ 0 ], rdict )
        print( *line )

print( "Complete" )
