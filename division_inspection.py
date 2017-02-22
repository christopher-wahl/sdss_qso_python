# Looking through the division catalog to find divided spectra which have average values ~ 1
# when divided by "53521-1714-011"
#
# i.e. looking for spectra which are about as bright (in flux space) as "53521-1714-011"
#
# Note: the results in divCat are UNSCALED - thus the data looking through here is UNSCALED
#
from common import freeze_support
from common.constants import BASE_PLOT_PATH


def main( ):
    from catalog import divCat
    from analysis.pipeline import results_pipeline

    namestring = "53521-1714-011"
    divCat = divCat[ namestring ]
    r_dict = { }
    for k, v in divCat.items( ):
        r_dict[ k ] = v[ 2 ]  # DivCat Format: slope, intercept, ave

    div_pipe = results_pipeline( results_range=(0.9, 1.1), results=r_dict )
    results = div_pipe.reduce_results( )
    for k, v in results.items( ):
        print( f"{k}: {v}" )
    print( len( results ) )

    from tools.plot import ab_z_plot

    ab_z_plot( BASE_PLOT_PATH, "test.pdf", namestring, div_pipe, "test" )


if __name__ == "__main__":
    freeze_support( )
    main( )