"""

    rtvLoadRadials



    HF-Radar Network
    Scripps Institution of Oceanography
    Coastal Observing Research and Development Center

"""

import datetime
import os
import sqlite3

import numpy as np
from rtvReadRadialFile import rtvReadRadialFile
from shapely.geometry import Point, Polygon


def rtvLoadRadials(c, logger, t):

    # Initialize return values
    r = []

    # Determine if we're reprocessing
    reprocessing = "reprocess" in c

    # Ensure radial selection consistent with previous run(s)
    if c.total.mpathfile and os.path.exists(c.total.mpathfile):
        if reprocessing:
            if not c.reprocess.lock:
                logger.error("Total mat-file exists. Should have been removed to ensure consistent results.")
                raise ValueError("rtvproc:rtvLoadRadials")
        else:
            try:
                last = np.load(c.total.mpathfile, allow_pickle=True).item()
                logger.debug(f"Loaded radial structure from prior run ({c.total.mpathfile})")
            except Exception as e:
                logger.alert(f"Failed to load radial structure from prior run ({c.total.mpathfile}): {str(e)}")
                logger.alert("Cannot ensure consistent radial selection if results are combined with previous run(s)")

    else:
        logger.debug(f"{c.total.mpathfile} not found, no pre-existing radial data")

    # Modify radial selection as needed based on previous run(s)
    if "last" in locals():
        nMod = 0
        for i, site in enumerate(c.site):
            siteMatch = np.where((last.r.network == site.network) & (last.r.site == site.name))[0]
            if not len(siteMatch):
                continue
            if len(siteMatch) > 1:
                logger.error(f"Found two records of radial data from {site.network}:{site.name} in previous radial data structure loaded from {c.total.mpathfile}")
                raise ValueError("rtvproc:rtvLoadRadials")
            if site.beampattern[0] != last.r[siteMatch[0]].patterntype:
                if last.r[siteMatch[0]].patterntype == "i":
                    site.beampattern = "ideal"
                elif last.r[siteMatch[0]].patterntype == "m":
                    site.beampattern = "measured"
                else:
                    logger.error(
                        f"Unknown beam pattern type '{last.r[siteMatch[0]].patterntype}' found for {site.network}:{site.name} \
                                 in previous radial data structure loaded from {c.total.mpathfile}"
                    )
                    raise ValueError("rtvproc:rtvLoadRadials")
                logger.notice(f"Modified {site.network}:{site.name} selection to use {site.beampattern} radials for consistency with previous run(s)")
                nMod += 1
            if site.useMinute != last.r[siteMatch[0]].t.minute:
                site.useMinute = last.r[siteMatch[0]].t.minute
                logger.notice(f"Modified {site.network}:{site.name} selection to use radials from {site.useMinute} minute(s) for consistency with previous run(s)")
                nMod += 1

        if nMod:
            logger.notice(f"{nMod} modifications made to radial site parameters based on previous runs")
        else:
            logger.debug("No modification needed to current radial config based on previous runs")

    # Build radial query
    sqlquery = f"SELECT FROM_UNIXTIME(r.time) AS t, n.net, s.sta, patterntype, file_arrival_time, lat, lon, range_res, range_bin_end, manufacturer, dfile, dir \
                 FROM radialfiles r JOIN network n ON n.network_id = r.network_id JOIN site s ON s.site_id = r.site_id WHERE FROM_UNIXTIME(r.time) >= \
                 '{t - datetime.timedelta(minutes=30)}' AND FROM_UNIXTIME(r.time) < '{t + datetime.timedelta(minutes=30)}'"
    if not reprocessing:
        sqlquery += f" AND r.file_arrival_time < '{c.rtv['new_state']}' "
    sqlquery += " AND ("
    nSite = len(c.site)
    for i, site in enumerate(c.site):
        sqlquery += f"(n.net = '{site.network}' AND s.sta = '{site.name}'"
        if site.beampattern[0] == "i":
            sqlquery += " AND r.patterntype = 'i' "
        elif site.beampattern[0] == "m":
            sqlquery += " AND r.patterntype = 'm' "
        else:
            logger.error(f"Unknown beam pattern type '{site.beampattern}'")
            raise ValueError("rtvproc:rtvLoadRadials")
        if site.useMinute == 0:
            tr = t
        elif 0 < site.useMinute < 30:
            tr = t + datetime.timedelta(minutes=site.useMinute)
        elif 30 <= site.useMinute < 60:
            tr = t - datetime.timedelta(minutes=60 - site.useMinute)
        else:
            logger.error(f"useMinute value of {site.useMinute} is out of range for site {site.network}:{site.name}. Value must [0-59]")
            raise ValueError("rtvproc:rtvLoadRadials:valueOutOfRange")
        sqlquery += f" AND FROM_UNIXTIME(FLOOR(r.time/60)*60) = '{tr}'"
        if i < nSite - 1:
            sqlquery += " OR "
        else:
            sqlquery += ")"

    # Submit Query
    conn = sqlite3.connect(c.raddb["url"], timeout=c.raddb["logintimeout"])
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    results = cursor.execute(sqlquery).fetchall()
    nRows = len(results)
    if not nRows:
        return c, r
    else:
        logger.debug(f"Site query returned {nRows} record(s)")

    # Rename result columns and convert to structure
    results = {k: [row[i] for row in results] for i, k in enumerate(results[0].keys())}
    q = [dict(zip(results.keys(), row)) for row in zip(*results.values())]

    # Log & remove any records that have NULL where data should be required
    rmRecordIndex = [False] * len(q)
    for i, row in enumerate(q):
        if not all([row[k] for k in ["file", "dir", "lat", "lon"]]) or (not reprocessing and not row["arrivaltime"]):
            rmRecordIndex[i] = True
            logger.warning(f"Radialfiles record {row['network']}:{row['site']}({row['beampattern']}) {row['t']} is missing required fields, removing from processing")

    q = [row for i, row in enumerate(q) if not rmRecordIndex[i]]
    nq = len(q)

    # Index new radials
    newRadialIndex = [True] * nq if reprocessing else [False] * nq
    if not reprocessing:
        for i, row in enumerate(q):
            if row["arrivaltime"] >= c.rtv["current_state"]:
                newRadialIndex[i] = True
                logger.debug(f"New radial from {row['network']}:{row['site']}({row['beampattern']}) arrived at {row['arrivaltime']}")

    nNewRadials = sum(newRadialIndex)
    if not nNewRadials:
        return
    if reprocessing:
        logger.info(f"{nNewRadials} radial(s) to be reprocessed")
    else:
        logger.info(f"{nNewRadials} new radial(s) to be processed")

    # Find sites that potentially overlap with new data
    loadRadialIndex = [False] * nq
    buf = 0.05
    sc = [(None, None)] * nNewRadials
    for i, row in enumerate(q):
        if not newRadialIndex[i]:
            continue
        if np.isnan(row["rangeend"]) or np.isnan(row["rangeres"]) or row["rangeend"] <= 0 or row["rangeres"] <= 0:
            row["siterange"] = 300 + c.rtv["grid_search_radius"]
            logger.notice(f"Missing radial range resolution or end from {row['network']}:{row['site']}, setting siterange to {row['siterange']} km")
        else:
            row["siterange"] = row["rangeres"] * row["rangeend"] + buf * row["rangeres"] + c.rtv["grid_search_radius"]
        sc[i] = (row["lat"], row["lon"], row["siterange"])

    for i, row in enumerate(q):
        if not newRadialIndex[i]:
            continue
        for j, other in enumerate(q):
            if i == j or loadRadialIndex[j]:
                continue
            range = Polygon.from_bounds(row["lon"] - row["siterange"], row["lat"] - row["siterange"], row["lon"] + row["siterange"], row["lat"] + row["siterange"])
            if Point(other["lon"], other["lat"]).within(range):
                loadRadialIndex[i] = True
                loadRadialIndex[j] = True
                break

    # Log results
    for i, row in enumerate(q):
        if not newRadialIndex[i]:
            continue
        if not loadRadialIndex[i]:
            logger.info(f"No overlap found with new data from {row['network']}:{row['site']}")

    nLoadRadials = sum(loadRadialIndex)
    if not nLoadRadials:
        logger.info("No potential data overlap with new radials")
        return
    logger.info(f"{nLoadRadials} radial files to be loaded for processing")

    # Obtain data from sites
    for i, row in enumerate(q):
        if not loadRadialIndex[i]:
            continue
        d = rtvReadRadialFile(row)
        logger.debug(f"Loaded {len(d.latitude)} radials from {row['file']}")

        # VFLG filtering
        if "vflag" in d:
            idx = d.vflag == 128
            nIdx = sum(idx)
            if nIdx > 0:
                d.latitude = np.delete(d.latitude, idx)
                d.longitude = np.delete(d.longitude, idx)
                d.speed = np.delete(d.speed, idx)
                d.heading = np.delete(d.heading, idx)
                if "range" in d:
                    d.range = np.delete(d.range, idx)
                logger.debug(f"Removed {nIdx} velocity flagged radials")
                if not len(d.latitude):
                    logger.info(f"No radial data left from {row['file']} after velocity flag filtering")
                    continue

        # Speed thresholding
        idx = np.abs(d.speed) > c.rtv["max_rad_speed"]
        nIdx = sum(idx)
        if nIdx > 0:
            d.latitude = np.delete(d.latitude, idx)
            d.longitude = np.delete(d.longitude, idx)
            d.speed = np.delete(d.speed, idx)
            d.heading = np.delete(d.heading, idx)
            if "range" in d:
                d.range = np.delete(d.range, idx)
            logger.debug(f"Removed {nIdx} radials with speed greater than {c.rtv['max_rad_speed']} cm/s")
            if not len(d.latitude):
                logger.info(f"No radial data left from {row['file']} after speed thresholding")
                continue

        # Landmasking
        dLim = [np.max(d.latitude), np.min(d.latitude), np.max(d.longitude), np.min(d.longitude)]
        nOverLand = 0
        for land in c.land:
            if (dLim[0] >= land.region[1]) and (dLim[1] <= land.region[0]) and (dLim[2] >= land.region[3]) and (dLim[3] <= land.region[2]):
                inside = np.where(Polygon.from_bounds(land.region).contains_points(np.column_stack((d.longitude, d.latitude))))[0]
                if len(inside):
                    d.latitude = np.delete(d.latitude, inside)
                    d.longitude = np.delete(d.longitude, inside)
                    d.speed = np.delete(d.speed, inside)
                    d.heading = np.delete(d.heading, inside)
                    if "range" in d:
                        d.range = np.delete(d.range, inside)
                    nOverLand += len(inside)

        if nOverLand > 0:
            logger.debug(f"Removed {nOverLand} radials falling over land")
            if not len(d.latitude):
                logger.info(f"No radial data left from {row['file']} after land masking")
                continue

        # Save loaded data
        r.append(
            {
                "isnew": newRadialIndex[i],
                "t": datetime.datetime.strptime(row["t"], "%Y-%m-%d %H:%M:%S.%f"),
                "network": row["network"],
                "site": row["site"],
                "sitelatitude": row["lat"],
                "sitelongitude": row["lon"],
                "patterntype": row["beampattern"],
                "manufacturer": row["manufacturer"],
                "file": row["file"],
                "dir": row["dir"],
                "latitude": d.latitude.tolist(),
                "longitude": d.longitude.tolist(),
                "speed": d.speed.tolist(),
                "heading": d.heading.tolist(),
            }
        )
        if "range" in d:
            maxrange = np.max(d.range) + buf * row["rangeres"] if not np.isnan(row["rangeres"]) else 300
            r[-1]["maxrange"] = maxrange

    return c, r
