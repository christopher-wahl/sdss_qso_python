
async def generic_async_wrapper( input_values, async_function, output_values = None ):
    """
    Basic asyncronous operations wrapper.  Be aware, no order will be maintained in this process.
    i.e. the results of output_values will very likely NOT correspond to those of input_values.

    input_values is a list of tuples. These values will be unpacked and passed to specified async_function

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

def generic_unordered_multiprocesser( input_values, multi_function, output_values = None, MAX_PROC = None ):
    from multiprocessing import Pool, cpu_count
    MAX_PROC = MAX_PROC or cpu_count()
    pool = Pool( processes = MAX_PROC )

    results = pool.imap_unordered( multi_function, input_values )
    pool.close()
    pool.join()

    if output_values is not None:
        for r in results:
            output_values.append( r )

def generic_ordered_multiprocesser( input_values, multi_function, output_values = None, MAX_PROC = None ):
    from multiprocessing import Pool, cpu_count
    MAX_PROC = MAX_PROC or cpu_count()
    pool = Pool( processes = MAX_PROC )

    results = pool.imap( multi_function, input_values )
    pool.close()
    pool.join()

    if output_values is not None:
        for r in results:
            output_values.append( r )

def generic_map_async_multiprocesser( input_values, multi_function, output_values = None, MAX_PROC = None ):
    from multiprocessing import Pool

    pool = Pool( processes = MAX_PROC )

    results = pool.map_async( multi_function, input_values )
    pool.close()
    pool.join()

    if output_values is not None:
        output_values.extend( results.get() )

