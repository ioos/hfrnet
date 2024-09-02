"""

    LTAMONTHLYAVG Compute monthly average velocity from sums

    A = ltaMonthlyAvg(c, logger, S) computes monthly average velocity
    fields and statistics from sums provided in S using a one-pass
    algorithm. Sums are filtered by the minimum monthly temporal coverage
    provided by the configuration structure before computing the average
    and variance fields.

    Inputs:
        c      - Dictionary containing configuration parameters
        logger - Logger object
        S      - Monthly sums

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
import numpy as np


def ltaMonthlyAvg(c, logger, S):

    # init return value
    A = {}

    # mask points below minimum temporal coverage
    min_coverage = c['lta']['min_month_temporal_coverage'] * 24
    mask = S['nGood'] < min_coverage
    if np.any(mask):
        S['nGood'][mask] = np.nan
        S['uSum'][mask] = np.nan
        S['vSum'][mask] = np.nan
        S['u2sum'][mask] = np.nan
        S['v2sum'][mask] = np.nan
        S['uMin'][mask] = np.nan
        S['vMin'][mask] = np.nan
        S['uMax'][mask] = np.nan
        S['vMax'][mask] = np.nan

    if not np.any(S['nGood']):
        logger.debug(f"Not enough data to meet minimum temporal coverage of {c['lta']['min_month_temporal_coverage']} days")
        return A

    # compute stats
    A = S.copy()
    A['uAvg'] = A['uSum'] / A['nGood']
    A['vAvg'] = A['vSum'] / A['nGood']
    A['uVar'] = (1 / (A['nGood'] - 1)) * (A['u2sum'] - ((1 / A['nGood']) * (A['uSum'] ** 2)))
    A['vVar'] = (1 / (A['nGood'] - 1)) * (A['v2sum'] - ((1 / A['nGood']) * (A['vSum'] ** 2)))

    logger.debug('Computed month average')

    return A
