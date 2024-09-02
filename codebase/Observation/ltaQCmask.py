"""

    LTAQCMASK Apply quality control masks to long-term average products

    A = ltaQCmask(logger, A, t, c)  ..masks spatial areas as a function 
                                      of time as needed.

    Developer Notes:
    Although input parameters t & c remain to be used yet, they will allow
    for time-dependent spatial masks and (sub)process-specific processing.

    See also LTAMONTHLY, LTAANNUAL


   HF-Radar Network
   Scripps Institution of Oceanography
   Coastal Observing Research and Development Center

"""
import numpy as np


def ltaQCmask(logger, A, t, c):

    # Filter out currents in the Straits of Florida
    # Do for all time until analysis show a good period,
    # either in the past or starting from some future date that we can keep.

    mask = (A['lat'] > 25) & (A['lat'] < 26.75) & (A['lon'] > -80.75) & (A['lon'] < -78.75)
    if np.any(mask):
        A['nGood'][mask] = np.nan
        A['uMin'][mask] = np.nan
        A['vMin'][mask] = np.nan
        A['uMax'][mask] = np.nan
        A['vMax'][mask] = np.nan
        A['uSum'][mask] = np.nan
        A['vSum'][mask] = np.nan
        A['u2sum'][mask] = np.nan
        A['v2sum'][mask] = np.nan
        A['uAvg'][mask] = np.nan
        A['vAvg'][mask] = np.nan
        A['uVar'][mask] = np.nan
        A['vVar'][mask] = np.nan

        logger.info(f"QC masked {np.sum(mask)} solutions in the Straits of Florida")

    return A
