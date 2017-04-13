from catalog import get_source_ns, load_shen_source, shenCat

data = load_shen_source()[ 1 ]

i = 0
for dp in data:
    ns = get_source_ns( dp )
    if ns in shenCat:
        shenCat[ ns ][ 'lum_mgii' ] = dp[ 83 ]
        shenCat[ ns ][ 'lum_mgii_err' ] = dp[ 84 ]
        shenCat[ ns ][ 'fwhm_mgii' ] = dp[ 85 ]
        shenCat[ ns ][ 'fwhm_mgii_err' ] = dp[ 86 ]
        i += 1
        print( f"{ns}: {i} : {shenCat[ ns ]}" )
