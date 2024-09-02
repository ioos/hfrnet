"""

    FINDNEWRTVS Obtain new RTVs

    t = find_new_rtvs(c, logger) returns a list of datetime objects corresponding
    to new RTV solutions as defined by process specific parameters for the
    maximum data age and state value. Messages are written to the logger
    and all other configuration properties are obtained from the
    dictionary c. The current and new (but not yet updated) state values
    are written to c for reference. It is up to the calling function to
    write the state value.

    Inputs:
        c      - Dictionary containing configuration parameters
        logger - Logger object

    Outputs:
        t  - List of datetime objects of new RTV files
        c[c['process']['name']]['current_state'] - Datetime of current
                                                   process state
        c[c['process']['name']]['new_state']     - Datetime of new (but not
                                                   updated) process state

    HF-Radar Network
    Scripps Institution of Oceanography
    Coastal Observing Research and Development Center


"""
import datetime
import State
import os
# import logging


def find_new_rtvs(c, logger):

    # initialize return values
    t = []
    c[c['process']['name']]['current_state'] = None
    c[c['process']['name']]['new_state'] = None

    # define RTV modification time search window

    # oldest RTV data time to consider for processing
    min_time = (datetime.datetime.now() - datetime.timedelta(hours=c[c['process']['name']]['max_age'])).replace(minute=0, second=0, microsecond=0)

    # Check state
    state = State(c['domain'], c['resolution'], c['process']['name'], c['confdb'])
    state.get()

    # Set start time to arbitrarily old value if no state is defined - let
    # min_time define new RTVs criteria
    if state.time is None:
        c[c['process']['name']]['current_state'] = datetime.datetime(1970, 1, 1)
        logger.info(f"No {c['process']['name']} state defined. Using maximum data age of {c[c['process']['name']]['max_age']} hours to find RTVs since {min_time}")
    else:
        c[c['process']['name']]['current_state'] = state.time
        logger.info(f"Obtained {c['process']['name']} state time of {c[c['process']['name']]['current_state']}")

    # Define the end time of the search window
    c[c['process']['name']]['new_state'] = datetime.datetime.now()
    logger.debug(f"RTV search window ends on {c[c['process']['name']]['new_state']}")

    # Search for new RTVs based on min data time and modification time window

    # Since the os.path.getmtime function returns a timestamp, convert state values to timestamp
    mod_min = c[c['process']['name']]['current_state'].timestamp()
    mod_max = c[c['process']['name']]['new_state'].timestamp()

    # Iterate over each hour since min_time
    n_new = 0
    current_time = min_time
    while current_time <= c[c['process']['name']]['new_state']:
        # Iteration specific config
        ci = c.copy()
        ci = ci['total']['getFilenames'](ci, current_time, 'rtv')  # generate rtv file names

        # Check file existence
        if os.path.isfile(ci['total']['mpathfile']):
            # Compare mod time to state values
            mod_time = os.path.getmtime(ci['total']['mpathfile'])
            if mod_min <= mod_time < mod_max:
                # Capture new RTV data times
                n_new += 1
                t.append(current_time)
                logger.debug(f"Found new RTV file {os.path.basename(ci['total']['mpathfile'])}")

        current_time += datetime.timedelta(hours=1)

    return t
