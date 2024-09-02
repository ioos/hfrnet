"""

    LTAANNUALAVG Compute annual average velocity from monthly sums

    A = ltaAnnualAvg(c, logger, year) computes annual average velocity
    fields and statistics from monthly sums using a one-pass
    algorithm. Sums are filtered by the minimum annual temporal coverage
    provided by the configuration structure before computing the average
    and variance fields.

    Inputs:
        c      - Dictionary containing configuration parameters
        logger - Logger object
        year   - Year for which to compute the averages

    Outputs:
        A - Dictionary containing the following fields:
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


    HF-Radar Network
    Scripps Institution of Oceanography
    Coastal Observing Research and Development Center


"""
import os
import numpy as np
import datetime
# import logging


def ltaAnnualAvg(c, logger, year):

    # Initialize return value
    A = {}

    # Iterate over each monthly sum file
    t = [datetime.datetime(year, month, 1) for month in range(1, 13)]

    S = {}
    nLoadedFiles = 0

    for ti in t:
        # Define sum file name
        filename = c['total'].getFilenames(c, ti, 'lta', 'month')

        # Check file exists
        if not os.path.isfile(filename):
            continue

        # Load file
        try:
            s = np.load(filename, allow_pickle=True).item()
            nLoadedFiles += 1
        except Exception as e:
            logger.error(f"Error loading {filename}: {str(e)}")
            continue

        logger.debug(f"Loaded {filename}")

        # Copy fields if no stats yet
        if not S:
            S = s
        # Otherwise, aggregate stat fields
        else:
            S['nGood'] = np.nansum([S['nGood'], s['nGood']], axis=0)
            S['uSum'] = np.nansum([S['uSum'], s['uSum']], axis=0)
            S['vSum'] = np.nansum([S['vSum'], s['vSum']], axis=0)
            S['u2sum'] = np.nansum([S['u2sum'], s['u2sum']], axis=0)
            S['v2sum'] = np.nansum([S['v2sum'], s['v2sum']], axis=0)
            S['uMin'] = np.minimum(S['uMin'], s['uMin'])
            S['vMin'] = np.minimum(S['vMin'], s['vMin'])
            S['uMax'] = np.maximum(S['uMax'], s['uMax'])
            S['vMax'] = np.maximum(S['vMax'], s['vMax'])

    if not S:
        logger.debug('No monthly data loaded')
        return A

    logger.debug(f"Summed values from {nLoadedFiles} monthly sum file(s)")

    # Mask points below minimum temporal coverage
    mask = S['nGood'] < c['lta']['min_year_temporal_coverage'] * 24

    if np.any(mask):
        for key in ['nGood', 'uSum', 'vSum', 'u2sum', 'v2sum', 'uMin', 'vMin', 'uMax', 'vMax']:
            S[key][mask] = np.nan

    if not np.any(S['nGood']):
        logger.debug(f"Not enough data to meet minimum temporal coverage of {c['lta']['min_year_temporal_coverage']} days")
        return A

    # Compute stats
    A = S
    A['uAvg'] = A['uSum'] / A['nGood']
    A['vAvg'] = A['vSum'] / A['nGood']
    A['uVar'] = (1 / (A['nGood'] - 1)) * (A['u2sum'] - ((1 / A['nGood']) * (A['uSum'] ** 2)))
    A['vVar'] = (1 / (A['nGood'] - 1)) * (A['v2sum'] - ((1 / A['nGood']) * (A['vSum'] ** 2)))

    logger.debug('Computed year average')

    return A
