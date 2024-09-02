"""

    RTVGETSITECONFIG Obtains time-dependent site configurations

    c = rtvGetSiteConfig(c, logger, t) obtains time-dependent HF-RADAR
    site configurations from the database for the domain, resolution, and
    time being processed.

    Required configuration structure fields are:

        domain
        resolution
        confdb

    Sites obtained and their parameters are written to the site field in
    the configuration structure c.

    See also RTV, LOGGER, DATABASE


    HF-Radar Network
    Scripps Institution of Oceanography
    Coastal Observing Research and Development Center

"""
# import logging
import mysql.connector
from mysql.connector import Error


def rtvGetSiteConfig(c, logger, t):

    # Connect to the configuration database
    try:
        conn = mysql.connector.connect(
            user=c['confdb']['user'],
            password=c['confdb']['password'],
            host=c['confdb']['url'],
            database='',
            connection_timeout=c['confdb']['logintimeout'],
            readonly=True
        )
    except Error as e:
        errmsg = 'Failed to connect to configuration database'
        if e.msg:
            errmsg = f"{errmsg}: {e.msg}"
        logger.error(errmsg)
        raise RuntimeError('rtvproc:rtvGetSiteConfig:dbConnectionFailed', errmsg)

    if not conn.is_connected():
        errmsg = 'Failed to connect to configuration database'
        logger.error(errmsg)
        raise RuntimeError('rtvproc:rtvGetSiteConfig:dbConnectionFailed', errmsg)

    # Build & execute query
    sqlquery = (
        "SELECT s.network, s.name, c.beampattern, c.use_radial_minute, s.id "
        "FROM site s "
        "JOIN site_config c ON c.site_id = s.id "
        "JOIN domain d ON c.domain_id = d.id "
        "JOIN resolution r ON c.resolution_id = r.id "
        f"WHERE d.name LIKE '{c['domain']}' "
        f"AND r.name LIKE '{c['resolution']}' "
        f"AND c.start_time <= '{t}' AND "
        f"(c.end_time > '{t}' OR c.end_time IS NULL)"
    )

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sqlquery)
        results = cursor.fetchall()
    except Error as e:
        errmsg = f"Configuration database query error: {e.msg}"
        logger.error(errmsg)
        raise RuntimeError('rtvproc:rtvGetSiteConfig:queryError', errmsg)
    finally:
        cursor.close()
        conn.close()

    nRows = len(results)

    if nRows == 0:
        # No sites configured
        return c

    elif nRows > 0:
        # Verify we got a unique list of sites (i.e. no duplicate configs for a given site)
        ids = [result['id'] for result in results]
        unique_ids = list(set(ids))
        if len(ids) != len(unique_ids):
            duplicate_ids = set(ids) - set(unique_ids)
            duplicate_sites = [result['name'] for result in results if result['id'] in duplicate_ids]
            errmsg = f"Found {len(duplicate_ids)} site(s) with overlapping configurations; {', '.join(duplicate_sites)}"
            logger.error(errmsg)
            raise RuntimeError('rtvproc:rtvGetSiteConfig:configError', errmsg)

        # Add each site
        c['site'] = []
        for result in results:
            site = {
                'network': result['network'],
                'name': result['name'],
                'beampattern': result['beampattern'],
                'useMinute': result['use_radial_minute']
            }

            # Check minute range
            if site['useMinute'] > 59:
                errmsg = f"{site['network']}:{site['name']} useMinute value of {site['useMinute']} is out of range. Valid range is [0-59]"
                logger.error(errmsg)
                raise RuntimeError('rtvproc:rtvGetSiteConfig:outOfRange', errmsg)

            c['site'].append(site)

    return c
