"""

    STC Sub-tidal current processing

    stc(c, logger) processes hourly total velocities to produce a
    sub-tidal current. Processing can be done in near real-time or as
    reprocessing.

    New totals are obtained based on state tracking in near real-time
    processing whereas processing times are provided in the configuration
    structure's reprocess field during reprocessing. The sub-tidal
    current is estimated by performing a 25-hour average for each time
    step obtained/provided. Solutions are saved to all configured formats
    which may include MAT, ASCII, and NetCDF files.

    State tracking is performed during near real-time processing only and
    is not used during reprocessing. The current and new state are
    obtained from findNewRtvs and the new state is written after
    all processing is completed.

    All logging is sent to the logger class.

    Developer Notes:
      May someday use harmonic analysis to remove tides or some other method.
      For now, based on 25-hour average.


    See also FINDNEWRTVS, STCCOMPUTE25HRAVG, SAVEMAT, SAVEASCII,
    STCSAVENETCDF, LOGGER, STATE


    HF-Radar Network
    Scripps Institution of Oceanography
    Coastal Observing Research and Development Center


"""
# import numpy as np
import pandas as pd
import State
import saveMat
import saveAscii
import stcSaveNetcdf
import stcCompute25hrAvg
from datetime import datetime, timedelta
from finNewRtvs import find_new_rtvs
# from collections import defaultdict


def stc(c, logger):

    # Determine if we're reprocessing
    reprocessing = 'reprocess' in c

    # Find new RTVs
    if reprocessing:
        if 'RTV' in c['processes']['name']:
            newRtvTimes = c['reprocess']('tNewRtvFiles')
        else:
            newRtvTimes = c['reprocess']('times')
    else:
        newRtvTimes = find_new_rtvs(c, logger)

    if len(newRtvTimes):
        logger.info(f"Obtained {len(newRtvTimes)} new RTVs between {min(newRtvTimes)} and {max(newRtvTimes)}")
    else:
        logger.info('No new RTVs found')
        return

    # Define STC hours to process
    processTimes = pd.to_datetime([])

    # Generate datetime vector of all 25-hour averages that need to be processed
    for t in newRtvTimes:
        processTimes = processTimes.append(pd.date_range(t - timedelta(hours=12), t + timedelta(hours=12), freq='H'))

    # Create a unique list
    processTimes = processTimes.drop_duplicates()

    # Truncate anything extending into the future
    processTimes = processTimes[processTimes <= datetime.now() - timedelta(hours=13)]

    # Check we have something to process
    if processTimes.empty:
        logger.info('No STCs to process')
        return
    else:
        logger.info(f"Found {len(processTimes)} STCs to process between {processTimes.min()} and {processTimes.max()}")

    # Iterate over each hour
    for tc in processTimes:
        if reprocessing:
            logger.info(f"Begin reprocessing stc for {tc}")
        else:
            logger.info(f"Begin processing stc for {tc}")

        # Iteration specific config
        ci = c.copy()

        # Compute Average
        A = stcCompute25hrAvg(ci, logger, tc)

        if A is None:
            logger.info('No average solutions returned')
            continue

        # Save data
        # Generate stc file names
        ci = ci['total'].getFilenames(ci, tc)

        # Get process (i.e. stc & method) specific metadata
        ci = ci.getExternalProcessMetadata(ci)

        # Save MAT file
        success, message = saveMat(ci, tc, A)

        if not success:
            errmsg = f"Error saving stc to mat-file; {message}"
            logger.error(errmsg)
            raise RuntimeError(f"rtvproc:stc: {errmsg}")

        logger.info('Saved stc solutions to mat-file')

        # Save ASCII file
        if 'ascii' in ci['process']('saveas').lower():
            success, message = saveAscii(ci, A)

            if not success:
                errmsg = f"Error saving stcs to ascii file; {message}"
                logger.error(errmsg)
                raise RuntimeError(f"rtvproc:stc: {errmsg}")

            logger.info('Saved stc solutions to ascii file')

        # Save NetCDF
        if 'netcdf' in ci['process']('saveas').lower():
            success, message = stcSaveNetcdf(ci, logger, tc, A)

            if not success:
                errmsg = f"Error saving stcs to netcdf file; {message}"
                logger.error(errmsg)
                raise RuntimeError(f"rtvproc:stc: {errmsg}")

            logger.info('Saved stc solutions to netcdf file')

    # Update state
    if not reprocessing:
        state = State(c['domain'], c['resolution'], 'stc', c['confdb'])
        state.get()
        state.time = c['stc']('new_state')
        state.write()
        logger.debug(f"Updated stc state to {state.time}")
        state.delete()


