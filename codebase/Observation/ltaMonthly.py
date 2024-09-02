"""

   LTAMONTHLY Monthly long-term average velocity processing

    ltaMonthly( c, logger ) iterates over each month to compute the
    average monthly velocity field using a one-pass algorithm.  Sums are
    first computed and saved to a MAT-file then averages are produced from
    the sums. Quality control spatial/temporal masks are applied, as
    needed, before saving output to configured formats which may include
    MAT, ASCII, and NetCDF.

    Reprocessing is indicated through the reprocess field in the
    configuration structure c.

    In both near real-time processing and reprocessing modes, there's a
    minimum month day defined which applies to the current month before
    which no average products will be made. Once the minimum month day for
    the current month is passed, the previous month will be eligible for
    processing.

    State tracking is performed during near real-time processing only and
    is not used during reprocessing.  The new state is written after all
    processing is completed.

    All logging is sent to the logger class.

    See also LTAMONTHSUM, LTAMONTHLYAVG, LTAQCMASK, SAVEMAT, SAVEASCII,
    LTASAVENETCDF, LTA, LOGGER, STATE

   HF-Radar Network
   Scripps Institution of Oceanography
   Coastal Observing Research and Development Center


"""
import datetime
import numpy as np
from state import State
from lta_qc_mask import ltaQCmask
from lta_monthly_sum import ltaMonthlySum
from lta_monthly_avg import ltaMonthlyAvg
from lta_save_netcdf import ltaSaveNetcdf
from save_ascii import saveAscii
from save_mat import saveMat
# from collections import defaultdict
# from logger import Logger


def ltaMonthly(c, logger):

    # Determine if we're reprocessing
    reprocessing = 'reprocess' in c

    # Determine Month(s) to Process
    timeNow = datetime.datetime.now()

    if reprocessing:
        # Define the start of the current month
        maxLtaDate = datetime.datetime(timeNow.year, timeNow.month, 1)

        # If we aren't past the min month day for monthly averages, shift date
        # back to the start of the previous month
        if not (timeNow.day >= c['lta']['monthly_min_month_day']):
            maxLtaDate = maxLtaDate - datetime.timedelta(days=maxLtaDate.day)

        # When RTV processing is enabled, determine if there are any averages
        # to (re)process based on rtvs that were reprocessed. Otherwise, use
        # the input time range for reprocessing.
        if 'RTV' in c['processes']['name']:
            newRtvTimes = c['reprocess']['tNewRtvFiles']
        else:
            newRtvTimes = c['reprocess']['times']

        # Determine if there are any averages to (re)process
        if len([t for t in newRtvTimes if t < maxLtaDate]) < 1:
            logger.debug(f'No new RTVs processed prior to {maxLtaDate}, exiting')
            return

        # Define month(s) to process
        processTimes = np.unique([t.replace(day=1) for t in newRtvTimes if t < maxLtaDate])
        processTimes = np.mean([processTimes, [t.replace(day=1) + datetime.timedelta(days=32) for t in processTimes]], axis=0)

        logger.info(f'Obtained {len(processTimes)} month(s) to process between {min(processTimes)} and {max(processTimes)}')

    else:
        # See if we've passed the minimum month day for processing
        if timeNow.day >= c['lta']['monthly_min_month_day']:
            # Determine if monthly average processing has already been run this
            # month (for the previous month)
            state = State(c['domain'], c['resolution'], 'lta-monthly', c['confdb'])
            state.get()

            if state.time and state.time.month == timeNow.month:
                logger.debug('Monthly LTA processing has already been run this month')
                return
        else:
            logger.debug(f'Below minimum month day ({c["lta"]["monthly_min_month_day"]}) for lta processing, exiting')
            return

        # Define month to process
        processTimes = [timeNow.replace(day=1) - datetime.timedelta(days=timeNow.day)]
        processTimes = np.mean([processTimes, [t.replace(day=1) + datetime.timedelta(days=32) for t in processTimes]], axis=0)

        logger.info(f'Obtained {len(processTimes)} month to process: {processTimes}')

    # Iterate over each month
    for tc in processTimes:
        if reprocessing:
            logger.info(f'Begin reprocessing monthly lta for {tc}')
        else:
            logger.info(f'Begin processing monthly lta for {tc}')

        # Iteration specific config
        ci = c.copy()

        # Define subprocess to differentiate monthly from annual processing
        ci['subprocess'] = {'name': 'month'}

        # Compute Sums
        S = ltaMonthlySum(ci, logger, tc)

        if not S:
            logger.info('No sums returned')
            continue

        # Save Sums to Mat-file
        ci = ci['total'].getFilenames(ci, tc)

        success, message = saveMat(ci, tc, S)
        if not success:
            errmsg = f'Error saving lta monthly sums to mat-file; {message}'
            logger.error(errmsg)
            raise RuntimeError(errmsg)

        logger.info('Saved lta monthly sums to mat-file')

        # Compute Average
        A = ltaMonthlyAvg(ci, logger, S)

        if not A:
            logger.info('No averaged data returned')
            continue

        # Save Average Mat-file
        ci = ci.getExternalProcessMetadata(ci)

        success, message = saveMat(ci, tc, A)
        if not success:
            errmsg = f'Error saving lta month average to mat-file; {message}'
            logger.error(errmsg)
            raise RuntimeError(errmsg)

        logger.info('Saved lta month to mat-file')

        # Apply QC filters
        A = ltaQCmask(logger, A, tc, c)
        if not A:
            logger.info('No averaged data remains after QC masking')
            continue

        # Save published files
        # Save ASCII file
        if 'ascii' in ci['process']['saveas'].lower():
            success, message = saveAscii(ci, A)
            if not success:
                errmsg = f'Error saving lta month to ascii file; {message}'
                logger.error(errmsg)
                raise RuntimeError(errmsg)

            logger.info('Saved lta month to ascii file')

        # Save NetCDF
        if 'netcdf' in ci['process']['saveas'].lower():
            success, message = ltaSaveNetcdf(ci, tc, A)
            if not success:
                errmsg = f'Error saving lta month to netcdf file; {message}'
                logger.error(errmsg)
                raise RuntimeError(errmsg)

            logger.info('Saved lta month to netcdf file')

    # Update state
    if not reprocessing:
        state.time = timeNow
        state.write()
        logger.debug(f'Updated lta monthly state to {state.time}')
        state.delete()
        del state
