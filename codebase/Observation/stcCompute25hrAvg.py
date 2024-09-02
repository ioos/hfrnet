"""

    STCCOMPUTE25HRAVG Compute 25-hour average velocity field

    A = stcCompute25hrAvg(c, logger, tc) computes the 25-hour average
    velocity field from the hourly rtv MAT files defined in the
    configuration structure for the center-time provided by tc.

    Hourly rtv solutions are filtered by the sub-tidal current's max_error
    HDOP threshold prior to processing. Locations which fall below the
    minimum temporal threshold (defined in min_temporal_coverage) are also
    masked. A one-pass sum of squares algorithm is used to compute the
    mean along with the number of solutions, minimum, maximum, and
    variance fields.

    Inputs:
        c      - Structure containing configuration parameters
        logger - Logger object
        tc     - Datetime (scalar) corresponding to 25-hr average center
                 time

    Outputs:
        A - dictionary containing the following fields:
            nGood: Number of observations
            uSum:  Sum of u
            vSum:  Sum of v
            u2Sum: Sum of u^2
            v2Sum: Sum of v^2
            uMin:  Minimum u
            uMax:  Maximum u
            vMin:  Minimum v
            vMax:  Maximum v
            uAvg:  Average u
            vAvg:  Average v
            uVar:  Variance u
            vVar:  Variance v

    All logging is sent to the logger class.

    See also STC, LOGGER


   HF-Radar Network
   Scripps Institution of Oceanography
   Coastal Observing Research and Development Center

"""
import os
import numpy as np
import pandas as pd
from datetime import timedelta


def stcCompute25hrAvg(c, logger, tc):

    # Initialize return value
    A = {}

    # Define RTV files to load based on center time
    t = pd.date_range(tc - timedelta(hours=12), tc + timedelta(hours=12), freq='H')

    # Iterate over each hourly RTV
    nLoadedFiles = 0
    for ti in t:
        # Define rtv file name
        c = c.total.getFilenames(c, ti, 'rtv')

        # Check file exists
        if not os.path.isfile(c.total.mpathfile):
            continue

        # Load file
        try:
            U = np.loadmat(c.total.mpathfile)['U']
            nLoadedFiles += 1
        except Exception as e:
            logger.alert(f"Error loading {c.total.mpathfile}: {str(e)}")
            continue

        logger.debug(f"Loaded {c.total.mpathfile}")

        # Filter by HDOP
        mask = U['hdop'] >= c.stc['max_error']
        if np.any(mask):
            U['u'][mask] = np.nan
            U['v'][mask] = np.nan

        # Initialize fields
        if not A:
            nGridPts = len(U['grid']['ocean_indices'])
            A['grid'] = U['grid']
            A['lat'] = U['lat']
            A['lon'] = U['lon']
            A['nGood'] = np.zeros(nGridPts)
            A['uSum'] = np.zeros(nGridPts)
            A['vSum'] = np.zeros(nGridPts)
            A['u2sum'] = np.zeros(nGridPts)
            A['v2sum'] = np.zeros(nGridPts)
            A['uMin'] = np.full(nGridPts, np.nan)
            A['vMin'] = np.full(nGridPts, np.nan)
            A['uMax'] = np.full(nGridPts, np.nan)
            A['vMax'] = np.full(nGridPts, np.nan)

        # Compute sums
        A['nGood'] += ~np.isnan(U['u'])
        A['uSum'] = np.nansum([A['uSum'], U['u']], axis=0)
        A['vSum'] = np.nansum([A['vSum'], U['v']], axis=0)
        A['u2sum'] = np.nansum([A['u2sum'], U['u']**2], axis=0)
        A['v2sum'] = np.nansum([A['v2sum'], U['v']**2], axis=0)
        A['uMin'] = np.nanmin([A['uMin'], U['u']], axis=0)
        A['vMin'] = np.nanmin([A['vMin'], U['v']], axis=0)
        A['uMax'] = np.nanmax([A['uMax'], U['u']], axis=0)
        A['vMax'] = np.nanmax([A['vMax'], U['v']], axis=0)

    # Mask points below minimum temporal coverage
    if nLoadedFiles < c.stc['min_temporal_coverage']:
        logger.debug(f"Minimum temporal coverage is {c.stc['min_temporal_coverage']} hours, only {nLoadedFiles} file(s) loaded")
        return {}

    mask = A['nGood'] < c.stc['min_temporal_coverage']
    if np.any(mask):
        A['nGood'][mask] = np.nan
        A['uSum'][mask] = np.nan
        A['vSum'][mask] = np.nan
        A['u2sum'][mask] = np.nan
        A['v2sum'][mask] = np.nan
        A['uMin'][mask] = np.nan
        A['vMin'][mask] = np.nan
        A['uMax'][mask] = np.nan
        A['vMax'][mask] = np.nan

    if not np.any(A['nGood']):
        logger.debug(f"Not enough data to meet minimum temporal coverage of {c.stc['min_temporal_coverage']} hours")
        return {}

    # Compute stats
    A['uAvg'] = A['uSum'] / A['nGood']
    A['vAvg'] = A['vSum'] / A['nGood']
    A['uVar'] = (1 / (A['nGood'] - 1)) * (A['u2sum'] - ((1 / A['nGood']) * (A['uSum']**2)))
    A['vVar'] = (1 / (A['nGood'] - 1)) * (A['v2sum'] - ((1 / A['nGood']) * (A['vSum']**2)))

    logger.debug(f"Computed average from {nLoadedFiles} files")

    return A
