from analysis.pipeline import redshift_ab_pipeline, speclist_analysis_pipeline
from catalog import divCat, shenCat
from common.constants import BASE_PLOT_PATH, BINNED_SPEC_PATH
from fileio.spec_load_write import async_load, bspecLoader


shenCat.load()

ns = "53521-1714-011"
z, ab, aberr = shenCat.subkey( ns, 'z', 'ab', 'ab_err' )
divCat.load( namestring=ns )


rmp = redshift_ab_pipeline( ns, z, ab, aberr, divCat[ ns ] )
rmp.reduce_results()
outd = rmp.bin_results()
rmp.plot_results( BASE_PLOT_PATH, f"{ns} Catalog Entries in Range.pdf")

bspecnames = list( rmp.get_results().keys() )
speclist = async_load( BINNED_SPEC_PATH, bspecnames, ".bspec")
prime = bspecLoader( ns )

chi_analysis = speclist_analysis_pipeline( prime, speclist,  )

print( "test")