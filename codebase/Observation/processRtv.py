"""

    processRTV


    HF-Radar Network
    Scripps Institution of Oceanography
    Coastal Observing Research and Development Center

"""
import time
import datetime
import FileLock
import Logger
# from collections import namedtuple, defaultdict
# from functools import partial


def processRtv(domain, resolution, configFunction, *args):

    # Initialize stopwatch
    ticValue = time.time()

    # Parse Input
    def validConfig(x):
        return callable(x)

    def validReproc(x):
        return isinstance(x, datetime.datetime) and x.year >= 1970

    # Parameters
    reprocessTimes = None
    reprocessLock = True

    if len(args) > 0:
        reprocessTimes = args[0]
    if len(args) > 1:
        reprocessLock = args[1]

    # Define options based on parsing
    configFunction = configFunction

    # Lowercase domain and resolution for consistency
    domain = domain.lower()
    resolution = resolution.lower()

    # Get processing configuration
    c = configFunction(domain, resolution)

    # Add reprocessing options
    if reprocessTimes is not None:
        c['reprocess'] = {
            'times': reprocessTimes,
            'lock': reprocessLock
        }

    # Configure logging
    logger = Logger(c['log']['file'])
    if 'level' in c['log']:
        logger.setLogLevel(c['log']['level'])
    if 'cmdWinLogLevel' in c['log']:
        logger.setCmdWinLogLevel(c['log']['cmdWinLogLevel'])

    # Process locking
    if 'reprocess' in c and not c['reprocess']['lock']:
        logger.info('Reprocessing without process locking')
    else:
        IPC = FileLock(c['lock']['file'])
        IPC.lock()
        if IPC.haveLock:
            logger.info(f'PID {IPC.ourPid} obtained lock')
        else:
            logger.info(f'PID {IPC.ourPid} cannot lock, PID {IPC.lockPid} has the lock')
            logger.delete()
            IPC.delete()
            return

    # Check process(es) obtained
    if 'processes' in c and c['processes']:
        logger.debug(f'Obtained {len(c["processes"])} processes')
    else:
        logger.notice('No processes obtained, exiting')
        return

    # Run process(es)
    logger.debug(f'Maximum number of computational threads: {1}')  # Placeholder for maxNumCompThreads

    c['process'] = {}
    for process in c['processes']:
        try:
            # Define process
            c['process']['name'] = process['name'].lower()
            c['process']['method'] = process['method'].lower()
            c['process']['methoddesc'] = process['description']
            c['process']['saveas'] = process['save_as']

            if c['process']['method'] != 'uwls':
                raise ValueError('Only uwls methods are supported')

            # Process specific code
            if c['process']['name'] == 'rtv':
                logger.info(f'Starting {c["process"]["method"]} {c["process"]["name"]} processing')
                tNewRtvFiles = rtv(c, logger)
                if not tNewRtvFiles:
                    logger.info('No rtv files created or updated')
                else:
                    logger.info(f'Created or updated {len(tNewRtvFiles)} rtv files')
                if 'reprocess' in c:
                    c['reprocess']['tNewRtvFiles'] = tNewRtvFiles

            elif c['process']['name'] == 'stc':
                logger.info(f'Starting {c["process"]["method"]} {c["process"]["name"]} processing')
                stc(c, logger)

            elif c['process']['name'] == 'lta':
                logger.info(f'Starting {c["process"]["method"]} {c["process"]["name"]} processing')
                lta(c, logger)

            else:
                logger.warning(f'Skipping undefined process "{c["process"]["name"]}"')

        except Exception as e:
            logger.error(f'Error processing {process["method"]} {process["name"]}: {str(e)}')

    # Clean up
    if 'IPC' in locals() and isinstance(IPC, FileLock):
        if IPC.haveLock:
            IPC.unlock()
            logger.info(f'PID {IPC.ourPid} unlocked')
        else:
            logger.notice(f'Our PID {IPC.ourPid} does not have lock on exit')
        IPC.delete()

    # Log elapsed time
    elapsedTime = time.time() - ticValue
    logger.info(f'Elapsed time {str(datetime.timedelta(seconds=elapsedTime))}')

    # Destroy logger object
    logger.delete


# Placeholder functions for rtv, stc, lta
def rtv(c, logger):
    return []


def stc(c, logger):
    pass


def lta(c, logger):
    pass
