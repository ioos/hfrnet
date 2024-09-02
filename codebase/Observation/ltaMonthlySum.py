"""

    LTAMONTHLYSUM Compute monthly one-pass sums of hourly rtv velocities

    S = ltaMonthlySum(c, logger, tc) computes monthly sums necessary for
    a one-pass averaging algorithm from hourly rtv solutions defined in
    the configuration structure c for the month tc.

    Hourly rtv solutions are filtered by the long-term average max_error
    HDOP threshold prior to processing.

    Inputs:
        c      - Dictionary containing configuration parameters
        logger - Logger object
        tc     - Datetime (scalar) corresponding to month to average

    Outputs:
        S - Dictionary containing the following fields:
            nGood: Number of observations
            uSum:  Sum of u
            vSum:  Sum of v
            u2Sum: Sum of u^2
            v2Sum: Sum of v^2
            uMin:  Minimum u
            uMax:  Maximum u
            vMin:  Minimum v
            vMax:  Maximum v

    All logging is sent to the logger class.

    See also LTAMONTHLY, LOGGER

   HF-Radar Network
   Scripps Institution of Oceanography
   Coastal Observing Research and Development Center

"""
# from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import os


def ltaMonthlySum(c, logger, tc):

    # Initialize return value
    S = {}

    # Define RTV files to load based on date provided
    t = pd.date_range(start=tc.replace(day=1), end=tc.replace(day=pd.Timestamp(tc.year, tc.month, 1).days_in_month, hour=23), freq='H')

    # Iterate over each hourly RTV
    nLoadedFiles = 0
    for ti in t:
        #
        # Define rtv file name
        # - THIS WILL NOT WORK: c is redefined at every iteration
        #
        c = c['total'].getFilenames(c, ti, 'rtv')

        # Check file exists
        if not os.path.isfile(c['total']['mpathfile']):
            continue

        # Load file
        try:
            U = np.load(c['total']['mpathfile'], allow_pickle=True).item()
            nLoadedFiles += 1
        except Exception as e:
            logger.alert(f"Error loading {c['total']['mpathfile']}: {str(e)}")
            continue

        logger.debug(f"Loaded {c['total']['mpathfile']}")

        # Filter by HDOP
        mask = U['hdop'] >= c['lta']['max_error']
        if np.any(mask):
            U['u'][mask] = np.nan
            U['v'][mask] = np.nan

        # Initialize fields
        if not S:
            nGridPts = len(U['grid']['ocean_indices'])
            S['grid'] = U['grid']
            S['lat'] = U['lat']
            S['lon'] = U['lon']
            S['nGood'] = np.zeros(nGridPts)
            S['uSum'] = np.zeros(nGridPts)
            S['vSum'] = np.zeros(nGridPts)
            S['u2sum'] = np.zeros(nGridPts)
            S['v2sum'] = np.zeros(nGridPts)
            S['uMin'] = np.full(nGridPts, np.nan)
            S['vMin'] = np.full(nGridPts, np.nan)
            S['uMax'] = np.full(nGridPts, np.nan)
            S['vMax'] = np.full(nGridPts, np.nan)

        # Compute sums
        S['nGood'] += ~np.isnan(U['u'])
        S['uSum'] = np.nansum(np.vstack([S['uSum'], U['u']]), axis=0)
        S['vSum'] = np.nansum(np.vstack([S['vSum'], U['v']]), axis=0)
        S['u2sum'] = np.nansum(np.vstack([S['u2sum'], U['u']**2]), axis=0)
        S['v2sum'] = np.nansum(np.vstack([S['v2sum'], U['v']**2]), axis=0)
        S['uMin'] = np.nanmin(np.vstack([S['uMin'], U['u']]), axis=0)
        S['vMin'] = np.nanmin(np.vstack([S['vMin'], U['v']]), axis=0)
        S['uMax'] = np.nanmax(np.vstack([S['uMax'], U['u']]), axis=0)
        S['vMax'] = np.nanmax(np.vstack([S['vMax'], U['v']]), axis=0)

    logger.debug(f"Summed values from {nLoadedFiles} hourly rtv files")

    return S
