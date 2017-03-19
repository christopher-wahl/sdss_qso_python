from analysis.chi import multi_chi_analysis
from catalog import shenCat
from common.constants import BASE_ANALYSIS_PATH, CHI_BASE_MAG, CONT_RANGE, MGII_RANGE, join
from fileio.list_dict_utils import namestring_dict_reader, namestring_dict_writer
from fileio.spec_load_write import async_rspec_scaled, text_write, write
from fileio.utils import fns, getFiles
from spectrum.utils import compose_speclist, flux_from_AB
from tools.list_dict import sort_list_by_shen_key
from tools.plot import ab_z_plot, four_by_four_multiplot, spectrum_plot


def composite_process( f ):
    ns = fns( f )
    print( ns )
    outpath = join( comppath, ns )

    indict = namestring_dict_reader( sourcepath, f )
    scaleflx = flux_from_AB( CHI_BASE_MAG )
    speclist = async_rspec_scaled( [ ns, *indict ], scaleflx )
    cspec = compose_speclist( speclist, f"Composite Base {ns}" )

    write( cspec, outpath, f"composite {ns}.rspec" )
    text_write( cspec, outpath, f"composite {ns}.text_spec" )
    spectrum_plot( cspec, outpath, f"Composite {ns}.pdf" )
    ab_z_plot( outpath, f"Source AB v Z {ns}.pdf", ns, indict )
    four_by_four_multiplot( cspec, speclist, outpath, f"Source Multiplot {ns}.pdf", plotTitle=f"Sources for {ns}" )
    speclist = sort_list_by_shen_key( async_rspec_scaled( shenCat, cspec ) )

    composite_limited = cspec.cpy( )
    composite_limited.trim( wl_range=MGII_RANGE )
    chilist = multi_chi_analysis( composite_limited, speclist, True )
    chilist = list( filter( lambda x: x[ 1 ] < MG_MAX, chilist ) )
    print( len( chilist ) )

    speclist = async_rspec_scaled( [ x[ 0 ] for x in chilist ], cspec )
    composite_limited = cspec.cpy( )
    composite_limited.trim( wl_range=CONT_RANGE )
    chilist = multi_chi_analysis( composite_limited, speclist, True )
    chilist = list( filter( lambda x: x[ 1 ] < 50, chilist ) )
    print( len( chilist ) )

    rdict = { }
    for c in chilist:
        rdict[ c[ 0 ] ] = shenCat[ c[ 0 ] ]
    namestring_dict_writer( rdict, outpath, f"Composite {ns} Results.csv" )
    ab_z_plot( outpath, f"Composite AB v Z {ns}.pdf", ns, rdict )
    speclist = async_rspec_scaled( [ x[ 0 ] for x in chilist ], cspec )
    four_by_four_multiplot( cspec, speclist, outpath, f"Composite {ns} 4x4.pdf", plotTitle=f"Composite {ns}" )


MG_MAX = 5
basepath = join( BASE_ANALYSIS_PATH, "EM 15 CONT 100 Old" )
sourcepath = join( basepath, "source" )
comppath = join( basepath, "Composites" )
ipath = join( basepath, "Individual Results" )

if __name__ == '__main__':
    filelist = sorted( getFiles( sourcepath, ".csv" ) )
    for f in filelist:
        print( f )
        if "-229.csv" in f:
            composite_process( f )
