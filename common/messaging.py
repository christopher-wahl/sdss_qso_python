"""
Simple messaging methods for better console output formatting
"""
import os
import sys


def tab_print( s: str, new_line: bool = True ) -> None:
    """
    Adds an intent to s before printing it.  If new_line = False, the line will not have a carriage return after printing.
    
    :param s: String to print
    :type s: str
    :param new_line: Whether or not to append a carriage return.  Defaults to True
    :type new_line: bool
    :return:
    :rtype: None
    """
    if new_line:
        print( f"       {s}" )
    else:
        print( f"       {s}", flush=True, end='' )


def unfinished_print( printline: str = "" ) -> None:
    """
    Prints a line without appending a carriage return.  Usually followed by calling done() after work is
    complete.
    
    :param printline: string to print 
    :type printline: str
    :return:
    :rtype: None
    """
    print( printline, end="", flush=True )


def done() -> None:
    """
    Intended to be used following unfinished_print() so that an action can be printed as started.  Afterwards, call
    done() and have " Done." printed and the carriage return appended.
    
    i.e.:
    
    Scaling spectra... Done.
    
    :return:
    :rtype: None
    """
    print( " Done.", end=linesep, flush=True )


""" CHARACTERS """
ANGSTROM = r"‎Å"
FLUX_UNITS = r"10^{-17} egs s^{-1} cm^{-2} %s^{-1}" % ANGSTROM
SQUARE = "²"
BETA = "β"
GAMMA = "γ"
linesep = os.linesep
PM = "±"
CHI = "χ²"

if sys.platform == "win32":
    def __fix_str( s: str ) -> str:
        return s.encode( 'cp1252', errors='replace' ).decode( 'cp1252' )


    ANGSTROM = __fix_str( ANGSTROM )
    FLUX_UNITS = __fix_str( FLUX_UNITS )
    BETA = __fix_str( BETA )
    GAMMA = __fix_str( GAMMA )
    PM = __fix_str( PM )
    CHI = __fix_str( CHI )
