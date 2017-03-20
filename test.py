from fileio.list_dict_utils import namestring_dict_reader
from fileio.spec_load_write import async_rspec_scaled, load, text_write

inpath, indat, inspec = "/home/christopher/Desktop/103/Composite/", "Composite Matches.dat", "composite.rspec"

cspec = load( inpath, inspec )
indat = namestring_dict_reader( inpath, indat )

speclist = async_rspec_scaled( indat.keys( ), cspec )

outpath = "/home/christopher/Desktop/103/Composite/Spec"
for spec in speclist:
    text_write( spec, outpath, f"{spec.getNS()}.text_rspec" )

with open( inpath + "list.txt", 'w' ) as outfile:
    outfile.write( 'speclist = "' )
    lines = ''.join( [ f"{spec.getNS()} " for spec in speclist ] )[ :-1 ] + '"'
    outfile.writelines( lines )
