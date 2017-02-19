from common.constants import linesep
from .catalog import catalog

shenCat = catalog( catalog.SHEN_CATALOG )
divCat = catalog( catalog.DIVIDE_CATALOG )
chiCat = catalog( catalog.CHI_CATALOG )


def get_shen_string( namestring: str, *append_values, CR: bool = False ) -> str:
    """
    Any values which are passed after namestring will be appended to the out_str in the
    order in which they are passed.  Appending method adds each value as f",{value}"

    If CR = True is passed, a carraige return will be appended at the end of the string.
    :param namestring:
    :param append_values:
    :return:
    """
    out_str = namestring
    for k in get_shen_subkeys( ):
        if k == "namestring":
            continue
        out_str += f",{shenCat.subkey( namestring, k )}"
    for v in append_values:
        out_str += f",{append_values}"
    if CR:
        out_str += linesep
    return out_str


def get_shen_subkeys( ):
    return [ "namestring", "ab", "ab_err", "bh_hb", "bh_hb_err", "bh_mgii", "bh_mgii_err", "gmag", "z" ]


def get_shen_header( CR: bool = False ):
    out_str = ''.join( f"{key}," for key in get_shen_subkeys( ) )[ :-1 ]
    if CR:
        out_str += linesep
    return out_str
