"""

    RTVGETPROCESSTIMES Obtain RTV times to process

    t = rtvGetProcessTimes(c, logger) returns a datetime list of hours that
    need to be processed for RTV solutions based on new radial data. Messages
    are written to the logger and all other configuration properties are
    obtained from the dictionary c. The current and new (but not yet updated)
    state values are written to c for reference. It is up to the calling
    function to write the state value.

    Inputs:
        c      - Dictionary containing configuration parameters
        logger - Logger object

    Outputs:
        t                         - Datetime list of RTV hours to be processed 
                                    based on availability of new radial data.
        c['rtv']['current_state'] - Datetime of current rtv state
        c['rtv']['new_state']     - Datetime of new (but not updated) rtv state


"""
import State
import datetime
# import logging
# import pandas as pd
from sqlalchemy import create_engine, text


def rtvGetProcessTimes(c, logger):

    # Initialize return values
    t = []
    c['rtv']['current_state'] = None
    c['rtv']['new_state'] = None

    # Define radial file arrival time search window
    minTime = (datetime.datetime.now() - datetime.timedelta(hours=c['rtv']['max_age'])).replace(minute=0, second=0, microsecond=0)
    minTime_str = minTime.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

    # Check state
    state = State(c['domain'], c['resolution'], 'rtv', c['confdb'])
    state.get()

    # Set start time to arbitrarily old value if no state is defined - let minTime select new radials
    if state.time is None:
        c['rtv']['current_state'] = datetime.datetime(1970, 1, 1)
        logger.info(f"No rtv state defined. Using maximum data age of {c['rtv']['max_age']} hours to find radials since {minTime_str}")
    else:
        c['rtv']['current_state'] = state.time
        logger.info(f"Obtained rtv state time of {c['rtv']['current_state']}")

    # Define the end time of the search window
    c['rtv']['new_state'] = (datetime.datetime.now() - datetime.timedelta(seconds=10)).replace(microsecond=0)
    logger.debug(f"Radial search window ends on {c['rtv']['new_state']}")

    # Find all sites associated with the domain and resolution
    conn_str = f"{c['confdb']['driver']}://{c['confdb']['user']}:{c['confdb']['password']}@{c['confdb']['url']}"
    engine = create_engine(conn_str, connect_args={'connect_timeout': c['confdb']['logintimeout']})

    try:
        with engine.connect() as conn:
            sqlquery = (
                "SELECT s.network, s.name"
                "FROM site s"
                "JOIN site_config c ON s.id = c.site_id"
                "JOIN domain d ON c.domain_id = d.id"
                "JOIN resolution r ON c.resolution_id = r.id"
                "WHERE d.name LIKE :domain"
                "AND r.name LIKE :resolution"
                "GROUP BY s.network, s.name"
            )
            results = conn.execute(sqlquery, domain=c['domain'], resolution=c['resolution']).fetchall()

    except Exception as e:
        errmsg = f"Database query error: {str(e)}"
        logger.error(errmsg)
        raise RuntimeError('rtvproc:rtvGetProcessTimes:dbQueryError', errmsg)

    if not results:
        errmsg = f"No sites defined for RTV {c['resolution']} {c['domain']} processing"
        logger.error(errmsg)
        raise RuntimeError('rtvproc:rtvGetProcessTimes:sitesNotDefined', errmsg)

    sites = [{'network': row['network'], 'name': row['name']} for row in results]
    logger.info(f"Found {len(sites)} sites associated with {c['domain']} {c['resolution']}")

    # Build radial query
    sqlquery = (
        "SELECT FROM_UNIXTIME(r.time)"
        "FROM radialfiles r"
        "JOIN network n ON n.network_id = r.network_id"
        "JOIN site s ON s.site_id = r.site_id"
        "WHERE (r.file_arrival_time >= :current_state"
        "AND r.file_arrival_time < :new_state)"
        "AND FROM_UNIXTIME(r.time) >= :min_time"
        "AND ("
    )
    site_conditions = " OR ".join([f"(n.net = '{site['network']}' AND s.sta = '{site['name']}')" for site in sites])
    sqlquery += site_conditions + ")"

    # Submit Query
    conn_str = f"{c['raddb']['driver']}://{c['raddb']['user']}:{c['raddb']['password']}@{c['raddb']['url']}"
    engine = create_engine(conn_str, connect_args={'connect_timeout': c['raddb']['logintimeout']})

    try:
        with engine.connect() as conn:
            results = conn.execute(text(sqlquery), current_state=c['rtv']['current_state'], new_state=c['rtv']['new_state'], min_time=minTime_str).fetchall()
    except Exception as e:
        errmsg = f"Database query error: {str(e)}"
        logger.error(errmsg)
        raise RuntimeError('rtvproc:rtvGetProcessTimes', errmsg)

    if not results:
        return t

    # Find unique dates (hours) to process
    times = [row[0] for row in results]
    times = [datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S.%f') for time in times]

    # Shift radials >= :30 to the top of the next hour
    times = [time.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(hours=1) if time.minute >= 30 else time.replace(minute=0, second=0, microsecond=0) for time in times]

    # Find unique values to process
    t = list(set(times))
    t.sort()

    return t


# Build radial query
#    sqlquery = f"""
#        SELECT FROM_UNIXTIME(r.time)
#        FROM radialfiles r
#        JOIN network n ON n.network_id = r.network_id
#        JOIN site s ON s.site_id = r.site_id
#        WHERE (r.file_arrival_time >= :current_state
#        AND r.file_arrival_time < :new_state)
#        AND FROM_UNIXTIME(r.time) >= :min_time
#        AND (
#    """
