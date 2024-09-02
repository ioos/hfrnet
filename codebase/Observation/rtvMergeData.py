"""

    RTVMERGETOTALS Merges current data with previous run(s)

    [r, U] = rtvMergeData(c, logger, r, U) merges radial and total data
    from the current run with previous runs and appends to the history.
    When reprocessing, an error is thrown if previous runs are found since
    it is expected that they have already been removed.

    See also RTV, LOGGER

    HF-Radar Network
    Scripps Institution of Oceanography
    Coastal Observing Research and Development Center

"""
import os
# import logging
import datetime
import scipy.io
import numpy as np


def rtvMergeData(c, logger, r, U):

    # . .. . ... .. . .. . ... .. . .. . ... .. . .. . ... ..
    # Nested function to create or append to rtv history
    def rtvHistory(msg):
        # hi = 0
        # if 'history' in U:
        #    hi = len(U['history'])
        U['history'].append({
            'timestamp': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'program': os.path.basename(__file__),
            'user': os.getenv('USER'),
            'message': msg
        })

    # Check for data file from previous run(s)
    if os.path.isfile(c['total']['mpathfile']):
        if 'reprocess' in c:
            # Error out if we're reprocessing
            errmsg = f"Total mat-file ({c['total']['mpathfile']}) exists. Should have been removed to ensure consistent results."
            if not c['reprocess']('lock'):
                errmsg += " Maybe a concurrent process is running? Try using process locking"
            logger.error(errmsg)
            raise RuntimeError(f"rtvproc:rtvMergeData: {errmsg}")
        else:
            # Load existing data
            try:
                last = scipy.io.loadmat(c['total']['mpathfile'])
                logger.debug(f"Loaded prior solutions from {c['total']['mpathfile']}")
            except Exception as e:
                logger.warning(f"Failed to load prior data from {c['total']['mpathfile']}: {str(e)}")
                logger.warning("Plan to overwrite existing file, data from previous run(s) will be lost")
    else:
        logger.debug(f"{c['total']['mpathfile']} not found, no prior solutions")

    # If no prior data, start history and return
    nNew = np.count_nonzero(np.isfinite(U['u']))
    if 'last' not in locals():
        rtvHistory(f"Saving {nNew} new solutions")
        logger.debug("Started history")
        return r, U

    # *Merge current run with prior data
    # .Loop over radial datasets from previous run(s)
    for p in range(len(last['r'])):
        #
        # and look for matching datasets in the current run.
        #
        site = last['r'][p]['site']
        network = last['r'][p]['network']
        patterntype = last['r'][p]['patterntype']
        for i in range(len(r)):
            siteMatch = [r[i]['site'] == site and r[i]['network'] == network and r[i]['patterntype'] == patterntype]

        # Append the radial dataset to the current run if it hasn't already been loaded
        if not any(siteMatch):
            n = len(r)
            r.append({})
            fields = last['r'][p].dtype.names
            for field in fields:
                r[n][field] = last['r'][p][field]

            logger.debug(f"Merged radial dataset from {last['r'][p]['network']} {last['r'][p]['site']} ({last['r'][p]['patterntype']})")

    # Find previous solutions that aren't being updated by new solutions
    osi = np.isnan(U['u']) & np.isfinite(last['U']['u'])

    if np.any(osi):
        # Keep previous solutions that aren't being updated by this run
        U['u'][osi] = last['U']['u'][osi]
        U['v'][osi] = last['U']['v'][osi]
        U['dopx'][osi] = last['U']['dopx'][osi]
        U['dopy'][osi] = last['U']['dopy'][osi]
        U['hdop'][osi] = last['U']['hdop'][osi]
        U['nRads'][osi] = last['U']['nRads'][osi]
        U['nSites'][osi] = last['U']['nSites'][osi]

    # Append to history
    U['history'] = last['U']['history']
    rtvHistory(f"Saving {np.count_nonzero(np.isfinite(U['u']))} solutions; {nNew} new or updated, {np.count_nonzero(osi)} unmodified from previous run(s)")
    logger.info(f"Updated history: {U['history'][-1]['message']}")

    return r, U
