from analysis.pipeline import get_chi_analysis_pipeline
from analysis.slope_fit import generic_log10_fit
from catalog import join_with_shen_cat, shenCat, sort_iterable_by_shen_key
from common.constants import BASE_ANALYSIS_PATH, CONT_RANGE, freeze_support
from common.messaging import CHI, PM, done, unfinished_print
from fileio.list_dict_utils import namestring_dict_reader, namestring_dict_writer
from fileio.spec_load_write import async_rspec_scaled, rspecLoader, text_write, write
from fileio.utils import dirCheck, fns, getFiles, join
from spectrum.utils import compose_speclist
from tools.plot import ab_z_plot, four_panel_multiplot


def main():
    """
    These were some spectra with interesting results from the full catalog search.  Their namestring dicts are kept
    in CSV files in the folder stored at interestpath below.
    
    For each file in that folder this process will:
        1. Load the CSV into a namestring dict
        2. Load both the primary spectrum from the matches (given by the file name) and the matching spectra from the
            namestring dict keys - scaled to the primary
        3. Form a composite spectrum out of all the Spectrum objects
        4. Fit a log function to the initial namestring dict results
        5. Create an output folder given by the primary namestring
        6. Plot the composite spectrum generated
        7. Plot an AB v Z graph of the initial namestring dict results with the fit line
        8. Plot a 4 panel chart of the primary spectrum and its initial matches
        9. Generate a chi^2 pipeline for the composite, run it against the entire catalog, reduce the results
        10. Join the results with data in shenCat to a namestring dict, write them to a CSV with the plots
        11. Fit the results to a log function
        12. Plot a 4-panel chart and an AB v Z chart for the composite and matching results
        
    This should provide a pretty good step-by-step example of a multitude of that the library can do, and how its
    moving parts can all come together.  It's a good idea to step through this by debugging it.
    """
    interestpath = join( BASE_ANALYSIS_PATH, "Matches of Interest" )
    outpath = join( interestpath, "Analysis" )
    max_chi = 0.5

    # define the function we'll be fitting to.
    def fit_func( x ):
        from numpy import log10
        return a * log10( x ) + b

    # Get the files of interest
    filelist = getFiles( interestpath )

    # Start looping through them
    for f in filelist:
        # Print a line to the console saying which file we're  working on.  This method doesn't put a carriage return
        # at the end, so when this process completes, we can print "Done." on the same line at the end.
        unfinished_print( f"Analyzing { fns(f) } matches..." )

        # Read in the namestring dict of the initial matches
        indict = namestring_dict_reader( interestpath, f )

        # load the primary spectrum and the matches from the namestring dict.  Scale them.  Add the primary to the
        # group of spectra being used to form a composite
        prime = rspecLoader( fns( f ) )
        speclist = async_rspec_scaled( indict, prime )
        speclist.insert( 0, prime )

        # define the output path for this set of data by just using the primary spectrum's namestring
        specoutpath = join( outpath, prime.getNS() )
        dirCheck(
                specoutpath )  # if the folder doesn't yet exist (it doesn't), create it.  Otherwise things will try to
        # write to folders than don't exist.  Clearly, that'd be a problem.


        # form the composite and write both its binary and textual format to the output folder
        composite = compose_speclist( speclist, f"Composite { prime.getNS() }" )
        write( composite, specoutpath, "composite.cspec" )
        text_write( composite, specoutpath, "composite.text_cspec" )

        del speclist  # Since we aren't exiting some method, python's garbage collector won't be triggered all that often
        # and large lists of large data are left to float about for a while.  This often results in the kernel dumping
        # a lot of data that won't be used again into the swap space on the hard drive - which is slow, but the kernel
        # doesn't know any better, since this is just looping.  Nothing to say, "we're done with this data."  It's easier
        # to just delete large arrays that won't be used again and eliminate that lost time, plus save up some swap.


        # Fit the log function, get constants and their uncertainties.  Just unpack the tuple directly and form a string
        # using those values.  This will go onto the AB v Z plots so we can see they actually are.
        (a, b), (a_uncert, b_uncert) = generic_log10_fit( [ shenCat[ ns ][ 'z' ] for ns in indict ],
                                                          [ shenCat[ ns ][ 'ab' ] for ns in indict ], True )
        fit_str = f"%0.2f { PM } %0.2f log10( x ) { '+' if b > 0 else '-' } %0.2f { PM } %0.2f" % (
            a, b, a_uncert, b_uncert)

        # Plot the composite
        composite.plot( specoutpath )

        # Plot the 4-panel chart of scaled matches to the primary (the ones that formed the composite), along with their
        # AB v Z, its fit, and since a primary was specified, the ab_v_z_plot will generate a modeled evolution as well
        # using tools.cosmo
        four_panel_multiplot( specoutpath, f"{prime.getNS()} Multiplot.pdf", prime, speclist,
                              f"Matches to { prime.getNS() }" )
        ab_z_plot( specoutpath, f"{ prime.getNS() } AB v Z.pdf", speclist, prime,
                   plotTitle=f" Matches to { prime.getNS() } {PM} 2 Sigma", rs_fit_func=fit_func, rs_fit_title=fit_str )

        # Get a chi^2 copy of an analysis_pipeline.  This method prebuilds a pipe specifically for chi^2 matching.
        # It's easier to just let the wrapper do it.  A raw pipe can also be built by using the class directly, but
        # the idea of loading and scaling, etc, can all be handled here.  This method returns a pipeline ready to do so.
        # You're welcome.
        pipeline = get_chi_analysis_pipeline( composite, shenCat, CONT_RANGE, max_chi )

        # So make it go.  This method - especially in this case where it's matching against the entire catalog - will
        # hit your processor as hard as it reasonably can (it's limited to a maximum number of processes equal to the
        # number of logical CPU cores you have.  The system won't lock or anything, but a lot of RAM will be used
        # and a lot of heat will be generated.  This will take ESPECIALLY long if you're running in DEBUG mode.  Go get
        # a cup of coffee or tell Dr. Monier some jokes.  Better yet - read that long write up I wrote for you.  Decode
        # my cryptic/manic ravings.  If you find typos, keep them to yourself.
        pipeline.do_analysis()

        # Now that the process is complete, cut down the number of results.  We've initialized the pipe to dump
        # everything that returns a chi^2 value > 0.5 (max_chi variable at the top).  If you don't reduce the results
        # and instead just call get_results() you'll get a namestring dict of ALL the results of ALL values.  That's not
        # a bad thing if you want to see what all the data looks like, but here it's not needed.
        results = pipeline.reduce_results()

        # These results are in the form { namestring : float }.  Give them their own key and position in a subdict
        # containing all the useful info in shenCat.  This way, when looing at the CSV later on, all the data is there.
        # This little method is pretty useful for pipeline results in that way.
        results = join_with_shen_cat( results, 'chi' )

        # Write the namestring dict to the disk in a CSV format.
        namestring_dict_writer( results, specoutpath, "composite matches.csv" )

        # Fit the resulting data, make the fit string for the plot, and plot it all
        (a, b), (a_uncert, b_uncert) = generic_log10_fit( [ shenCat[ ns ][ 'z' ] for ns in indict ],
                                                          [ shenCat[ ns ][ 'ab' ] for ns in indict ], True )
        fit_str = f"%0.2f { PM } %0.2f log10( x ) { '+' if b > 0 else '-' } %0.2f { PM } %0.2f" % (
            a, b, a_uncert, b_uncert)

        ab_z_plot( specoutpath, "Composite AB Z.pdf", results,
                   plotTitle=f"Composite Matches: Maximum {CHI} = {max_chi}", rs_fit_func=fit_func,
                   rs_fit_title=fit_str )
        # Will need to load up the spectra that matched for the 4-panel plot.  This method both loades them
        # up and scales them to the spectrum they're given.  The sort_iterable... one returns a list of namestrings
        # sorted by redshift (by default - can use ther shenCat keys if desired).
        # The scale_to factor in async_rsepc_scaled can also be a flux density value if desired
        results = async_rspec_scaled( sort_iterable_by_shen_key( results ), scale_to=composite )
        four_panel_multiplot( specoutpath, f"Composite Matches Multiplot.pdf", composite, results,
                              f"Matches to Composite Spectrum: Maximum {CHI} = {max_chi} " )
        done()  # print a pretty "Done." to the console

        # Be proactive with your memory.  Real Python programmers would probably hate that I do this.  They'd tell me
        # to wrap all this into a submethod and call that and let the garbage collector handle it all.  They're probably
        # right, but oh well.  I've already gone this far.
        del results, pipeline


if __name__ == "__main__":
    freeze_support()  # Windows requirement for multiprocessing.  Must be used in the entry file of a program.
    # It actually comes from multiprocessing.freeze_support, but I keep a link in common.constants
    # since I'm always importing from there anyway.  Quick access.

    # The try, except isn't needed, but it makes the explosion of stuff dropped to the console when tapping CTRL+C
    # a little easier to stomach (if your timing is good.  During multiprocessing methods, not so much).
    try:
        main()
    except KeyboardInterrupt:
        print( "Keyboard Break." )
