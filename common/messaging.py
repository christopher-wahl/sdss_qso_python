
def KeyErrorString( function, key, value ):
    return "Unknown key value in %s( **kwargs )\nKey: %s\nValue: %s" % ( function, key, value )