
def KeyErrorString( function, key, value ):
    return "Unknown key value in %s( **kwargs )\nKey: %s\nValue: %s" % ( function, key, value )


def tab_print( s: str, new_line: bool = True ) -> None:
    if new_line:
        print( f"       {s}" )
    else:
        print( f"       {s}", end='' )
