
class analysis_pipeline:

    __primeSpec = None
    __speclist = None
    __analysis_func = None
    __result_low = None
    __result_high = None

    def __init__(self, primeSpec, speclist, analysis_function, result_range, binWidth = 0.01 ):
        self.__primeSpec = primeSpec
        self.__speclist = speclist
        self.__analysis_func = analysis_function
        self.__result_low, self.__result_high = result_range