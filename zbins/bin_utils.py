def genBinLabels( step = 0.01, minZ = 0.46, maxZ = 0.82 ):
    strlist = []
    while( minZ < maxZ):
        strlist.append( binString( minZ, step ) )
        minZ += step
    return strlist

def binString( z, step ):
    fstr = f"%0.{ len( str( step - int( step ) )[ 2: ]) }f"
    return "z" + fstr % z + "-" + fstr % ( z + step )

def getBinString( z, minZ = 0.46, maxZ = 0.82, step = 0.01 ):
    while( minZ + step <= z and minZ + step < maxZ ):
        minZ += step
    if minZ == maxZ:
        minZ -= step
    return binString( minZ, step )

def getBinRange( bin_string ):
    bin_string = bin_string[ 1: ]
    bin_string = bin_string.split( "-" )
    return float( bin_string[ 0 ] ), float( bin_string[ 1 ][ 1: ] )