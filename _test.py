from catalog import get_source_ns, load_shen_source, shenCat

data = load_shen_source()[ 1 ]

i = 0
for dp in data:
    ns = get_source_ns( dp )
    if ns in shenCat:
        # shenCat[ ns ][ 'lum_mgii' ] = dp[ 89 ]
        # shenCat[ ns ][ 'lum_mgii_err' ] = dp[ 90 ]
        # shenCat[ ns ][ 'ew_mgii' ] = dp[ 93 ]
        # shenCat[ ns ][ 'ew_mgii_err' ] = dp[ 94 ]
        d = { 'lum_mgii': dp[ 89 ], 'lum_mgii_err': dp[ 90 ], 'ew_mgii': dp[ 93 ], 'ew_mgii_err': dp[ 94 ],
              'lum_hb': dp[ 55 ], 'lum_hb_err': dp[ 56 ], 'ew_hb': dp[ 59 ], 'ew_hb_err': dp[ 60 ] }
        n = shenCat[ ns ]
        n.update( d )
        shenCat[ ns ] = n
        i += 1
        ks = sorted( n.keys() )
        print( f"{i} / {len( shenCat )}" )
# shenCat.rewrite()
print( "Rewritten." )
# shenCat.export_text()
print( "Exported." )
