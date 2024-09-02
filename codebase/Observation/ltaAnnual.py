"""

    LTAANNUAL Annual long-term average velocity processing

    ltaAnnual(c, logger) iterates over each year to compute the
    average annual velocity field using a one-pass algorithm.

    Annual sums are computed from monthly sum files which are used to
    compute averages and statistics. Quality control spatial/temporal
    masks are applied, as needed, before saving output to configured
    formats which may include MAT, ASCII, and NetCDF.

    Reprocessing is indicated through the reprocess field in the
    configuration structure c.

    In both near real-time processing and reprocessing modes, there's a
    minimum date defined which applies to the current year before
    which no average products will be made. Once the minimum date for
    the current year is passed, the previous year will be eligible for
    processing.

    State tracking is performed during near real-time processing only and
    is not used during reprocessing. The new state is written after all
    processing is completed.

    All logging is sent to the logger class.

    See also LTAANNUALAVG, LTAQCMASK, SAVEMAT, SAVEASCII, LTASAVENETCDF,
    LTA, LOGGER, STATE


    HF-Radar Network
    Scripps Institution of Oceanography
    Coastal Observing Research and Development Center


"""
import State
import datetime
import ltaQCmask
import ltaAnnualAvg
import ltaSaveNetcdf
import saveAscii
import saveMat
import pandas as pd
# import numpy as np
# from collections import defaultdict


def ltaAnnual(c, logger):

    # Determine if we're reprocessing
    reprocessing = 'reprocess' in c

    # Determine Year(s) to Process
    timeNow = datetime.datetime.now()

    if reprocessing:
        # Define the start of the current year
        maxLtaDate = datetime.datetime(timeNow.year, 1, 1)

        # If we aren't past the min date for annual averages, shift date
        # back to the start of the previous year
        if not (timeNow >= c['lta']['annual_min_date']):
            maxLtaDate = maxLtaDate - pd.DateOffset(years=1)

        # When RTV processing is enabled, determine if there are any averages
        # to (re)process based on rtvs that were reprocessed. Otherwise, use
        # the input time range for reprocessing.
        if 'RTV' in c['processes']['name']:
            newRtvTimes = c['reprocess']['tNewRtvFiles']
        else:
            newRtvTimes = c['reprocess']['times']

        # Determine if there are any averages to (re)process
        if not any(newRtvTimes < maxLtaDate):
            logger.debug(f'No new RTVs processed prior to {maxLtaDate}, exiting')
            return

        # Define year(s) to process
        processTimes = pd.to_datetime(newRtvTimes[newRtvTimes < maxLtaDate]).to_period('Y').unique()
        processTimes = pd.to_datetime([pt.start_time for pt in processTimes])

        logger.info(f'Obtained {len(processTimes)} year(s) to process between {min(processTimes)} and {max(processTimes)}')

    else:
        # See if we've passed the minimum date for processing
        if timeNow >= c['lta']['annual_min_date']:
            # Determine if monthly average processing has already been run this
            # year (for the previous year)
            state = State(c['domain'], c['resolution'], 'lta-annual', c['confdb'])
            state.get()

            if state.time and state.time.year == timeNow.year:
                logger.debug('Annual LTA processing has already been run this year')
                return
        else:
            logger.debug(f"Prior to minimum date ({c['lta']['annual_min_date'].strftime('%b %d, %Y')}) for annual lta processing, exiting")
            return

        # Define year to process
        processTimes = pd.to_datetime([timeNow - pd.DateOffset(years=1)])

        logger.info(f'Obtained {len(processTimes)} year to process: {processTimes[0].year}')

    # Iterate over each year
    for tc in processTimes:
        if reprocessing:
            logger.info(f'Begin reprocessing annual lta for {tc.year}')
        else:
            logger.info(f'Begin processing annual lta for {tc.year}')

        # Iteration specific config
        ci = c.copy()

        # Define subprocess to differentiate monthly from annual processing
        ci['subprocess'] = {'name': 'year'}

        # Compute Average
        A = ltaAnnualAvg(ci, logger, tc.year)

        if A is None:
            logger.info('No averaged data returned')
            continue

        # Save Average Mat-file
        ci = ci['total'].getFilenames(ci, tc)
        ci = ci.getExternalProcessMetadata(ci)

        success, message = saveMat(ci, tc, A)

        if not success:
            errmsg = f'Error saving lta year average to mat-file; {message}'
            logger.error(errmsg)
            raise RuntimeError(f'rtvproc:ltaAnnual: {errmsg}')

        logger.info('Saved lta year to mat-file')

        # Apply QC filters
        A = ltaQCmask(logger, A, tc, c)

        if A is None:
            logger.info('No averaged data remains after QC masking')
            continue

        # Save published files
        # Save ASCII file
        if 'ascii' in ci['process']['saveas'].lower():
            success, message = saveAscii(ci, A)

            if not success:
                errmsg = f'Error saving lta year to ascii file; {message}'
                logger.error(errmsg)
                raise RuntimeError(f'rtvproc:ltaAnnual: {errmsg}')

            logger.info('Saved lta year to ascii file')

        # Save NetCDF
        if 'netcdf' in ci['process']['saveas'].lower():
            success, message = ltaSaveNetcdf(ci, tc, A)

            if not success:
                errmsg = f'Error saving lta year to netcdf file; {message}'
                logger.error(errmsg)
                raise RuntimeError(f'rtvproc:ltaAnnual: {errmsg}')

            logger.info('Saved lta year to netcdf file')

    # Update state
    if not reprocessing:
        state.time = timeNow
        state.write()
        logger.debug(f'Updated lta annual state to {state.time}')
        state.delete()
        del state
