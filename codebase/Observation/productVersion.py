"""
    
    PRODUCTVERSION Returns the rtvproc product version

    v = product_version(process) given process name and method in the
    process dictionary, the product version is returned as a string corresponding
    to the format 'major.minor.maintenance'.

    Any changes to grids, processing algorithms, or anything that would
    alter the product(s) should be reflected by the version.

    Supported processes are rtv, stc and lta. Only the unweighted
    least-squares method (uwls) is supported.

    HF-Radar Network
    Scripps Institution of Oceanography
    Coastal Observing Research and Development Center

"""


def product_version(process):

    if process['name'] == 'rtv':
        if process['method'] == 'uwls':
            v = '2.0.00'
    elif process['name'] == 'stc':
        if process['method'] == 'uwls':
            v = '2.0.00'
    elif process['name'] == 'lta':
        if process['method'] == 'uwls':
            v = '2.0.00'
    else:
        v = None

    if v is None:
        raise ValueError(f"Process '{process['name']}' and/or method '{process['method']}' not recognized for defining the product version")

    return v


