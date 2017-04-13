"""
This package contains generic multiprocessing methods.  The goal of each is the same: to provide a generic outline
 for invoking some kind of multiprocessing technique, operating some multi_function over a list of input values and
 possibly providing output values (if desired).

The basic outline is that the user defines some multi_function such that it takes some singular input value inputV,
 performs an operation, and if desired returns a value.  If method requires more than one value to be passed, they should
 all be collectively passed as a tuple of ( val1, val2, ... ), then unpacked within the multi_function.

        def multi_function( inputV ) -> float
            val1, val2 = inputV
            return val1 + val2

The total list of values over which to operate should be passed in as input_values.  If it is necessary to form each 
 set of values as a tuple (as above), then they should be packed prior to being passed to the generic multiprocessor.

If output values from the multifunction are desired, they will be appended to a passed output_values list.  NOTICE: If
 an output_list is not provided, NO values will be returned directly from the operation as all of these methods do not
 return anything.

Should the order of operation, or the order of output values, matter - make used of the generic_unordered_multiprocessor.
 The _unordered_ method operates the same pool.imap feature, but does not require ordered operations and so no order is
 guaranteed.

The pool.imap methods generally low impact in memory, as the results are pulled out of the pool as soon as they arrive.
 However, often times the pool.map_async process is faster to use.  However, as the entire process runs until the pool
 is completely done, memeory use is substantial for large operations.  If RAM is not a restriction (or the process is
 small),then the _map_async_ method may be desirable.  Notice, this async method implies no guaranteed order and order
 should not be expected.
 
All methods make use of the same passing structure (with the exception of the generic_async_wrapper, which is more useful
 for writing/reading the disk and does not use Pool, so does not take a MAX_PROC value), so they can be used
 interchangably simply without any need to change the values passed, their order, typing, etc.
"""
from typing import Callable, Iterable


async def generic_async_wrapper( input_values: Iterable, async_function: Callable, output_values: list = None ) -> None:
    """
    Basic asyncronous operations wrapper.  Be aware, no order will be maintained in this process.
    i.e. the results of output_values will very likely NOT correspond to those of input_values.

    input_values is a list of tuples. These values will be unpacked and passed to specified async_function

    SEE NOTES AT THE TOP OF THE tools.async_tools PACKAGE FOR MORE INFORMATION ON HOW TO USE THE generic_ MULTIPROCESS
    METHODS
    
    Note:  No results are returned directly by this method.  Returned results of async_function are appended to output_values.
    If output_values is not given, no results will be returned from this method.

    :param input_values: list of tuples [ (val1, val2...), ... ] to be passed to async_function by async_function( *(val1, val2...) )
    :param async_function: asyncronous method which contains the actual operation to be performed.
    :param output_values: If passed in, results returned by async_function will be appended to this list.
    :type input_values: list
    :type async_function: function
    :type output_values: list
    :return: None
    :rtype: None
    """
    import asyncio

    coroutines = [ async_function( *input_value ) for input_value in input_values ]
    completed, pending = await asyncio.wait( coroutines )

    if output_values is not None:
        output_values.extend( [ result.result() for result in completed ] )


def generic_unordered_multiprocesser( input_values: Iterable, multi_function: Callable, output_values: list = None,
                                      MAX_PROC: int = None ) -> None:
    """
    SEE NOTES AT THE TOP OF THE tools.async_tools PACKAGE FOR MORE INFORMATION ON HOW TO USE THE generic_ MULTIPROCESS
    METHODS
    
    :param input_values: Iterable of values to pass to multi_function 
    :param multi_function: Callable which accepts only one input value, which will be passed from input_values
    :param output_values: If output values are desired, they will be gathered here.
    :param MAX_PROC: Maxmium number of concurrent processed - will be passed to Pool().  Defaults to cpu_count()
    :type input_values: list
    :type multi_function: Callable
    :type output_values: list
    :type MAX_PROC: int
    :return: None
    :rtype: None
    """
    from multiprocessing import Pool, cpu_count
    MAX_PROC = MAX_PROC or cpu_count()
    pool = Pool( processes = MAX_PROC )

    results = pool.imap_unordered( multi_function, input_values )
    pool.close()
    pool.join()

    if output_values is not None:
        for r in results:
            output_values.append( r )

    del pool


def generic_ordered_multiprocesser( input_values: Iterable, multi_function: Callable, output_values: list = None,
                                    MAX_PROC: int = None ) -> None:
    """
    SEE NOTES AT THE TOP OF THE tools.async_tools PACKAGE FOR MORE INFORMATION ON HOW TO USE THE generic_ MULTIPROCESS
    METHODS

    :param input_values: Iterable of values to pass to multi_function 
    :param multi_function: Callable which accepts only one input value, which will be passed from input_values
    :param output_values: If output values are desired, they will be gathered here.
    :param MAX_PROC: Maxmium number of concurrent processed - will be passed to Pool().  Defaults to cpu_count()
    :type input_values: list
    :type multi_function: Callable
    :type output_values: list
    :type MAX_PROC: int
    :return: None
    :rtype: None
    """
    from multiprocessing import Pool, cpu_count
    MAX_PROC = MAX_PROC or cpu_count()
    pool = Pool( processes = MAX_PROC )

    results = pool.imap( multi_function, input_values )
    pool.close()
    pool.join()

    if output_values is not None:
        for r in results:
            output_values.append( r )

    del pool


def generic_map_async_multiprocesser( input_values: Iterable, multi_function: Callable, output_values: list = None,
                                      MAX_PROC: int = None ) -> None:
    """
    SEE NOTES AT THE TOP OF THE tools.async_tools PACKAGE FOR MORE INFORMATION ON HOW TO USE THE generic_ MULTIPROCESS
    METHODS

    :param input_values: Iterable of values to pass to multi_function 
    :param multi_function: Callable which accepts only one input value, which will be passed from input_values
    :param output_values: If output values are desired, they will be gathered here.
    :param MAX_PROC: Maxmium number of concurrent processed - will be passed to Pool().  Defaults to cpu_count()
    :type input_values: list
    :type multi_function: Callable
    :type output_values: list
    :type MAX_PROC: int
    :return: None
    :rtype: None
    """
    from multiprocessing import Pool

    pool = Pool( processes = MAX_PROC )

    results = pool.map_async( multi_function, input_values )
    pool.close()
    pool.join()

    if output_values is not None:
        output_values.extend( results.get() )

    del pool

