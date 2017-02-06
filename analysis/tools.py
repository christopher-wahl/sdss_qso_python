
def paired_list_to_dict( paired_list ):
    """
    Converts a list of [ ( a, b ), ( c, d ) ... ] or [ { a : b }, { c : d } ... ]
    to a dictionary: {  a : b, c : d ... }

    If the entires of paired_list are not either a dictionary or a tuple/list of length 2, raises Attribute Error

    :param paired_list:
    :return:
    """
    def __err():
        raise TypeError(
            "paired_list_to_dict: paired_list entries must be either dict or have a length of 2\nFirst entry: %s" %
            paired_list[ 0 ] )

    out_dict = {}
    for point in paired_list:
        if type( point ) == dict:
            out_dict.update( point )
        elif len( paired_list[ 0 ] ) == 2:
            out_dict.update( { point[ 0 ] : point[ 1 ] } )
        else: __err()

    return out_dict