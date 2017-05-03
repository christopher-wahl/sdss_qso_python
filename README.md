This is the code underlaying a research project conducted (initially) by Christopher Wahl while an undergraduate physics major at the College at Brockport. For a more thorough understanding of the project itself, see the project writeup in the Documentation folder.

Python 3.6 is a minimum requirement, resulting from extensive use of `f"{...}"` formatted strings.  Linux is highly recommended, though not a hard requirement - provisions do exist for Windows.  The AstroPy, SciPy and NumPy packages are used often throughout the library.

Multiprocessing tools and generic wrappers are available in the `tools.async_tools` package.  See the documentation are the top of the package for further instruction on their use. 

Note:  The tools.plot package relies upon an installation of the Python 3 modified [Gnuplot-py](https://github.com/oblalex/gnuplot.py-py3k).

The data upon which this library was built is available in the [SDSS_QSO_DATA](https://github.com/christopher-wahl/sdss_qso_data) repository.