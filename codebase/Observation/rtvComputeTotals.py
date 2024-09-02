"""

    RTVCOMPUTETOTALS Computes total solutions from radial velocities

    U = rtvComputeTotals(c, logger, r) returns a structure containing
    total velocity solutions computed from radial velocity measurements
    using input processing parameters.

    Inputs:
        c      - Configuration structure
        logger - Logger object
        r      - Radial data structure

    Outputs:
        U - Total solution structure with fields:
            lat
            lon
            u
            v
            dopx
            dopy
            hdop
            nRads
            nSites
            grid
                resolution_km
                projection
                x_range
                y_range
                dx
                dy
                size
                ocean_indices


"""
import numpy as np
# from scipy.spatial import Delaunay
# from math import radians, cos, sin, asin, sqrt


def rtvComputeTotals(c, logger, r):

    # initialize return values
    #
    U = {}

    # reduce total grid solution space
    #
    gridAllRadCount = np.zeros(len(c.grid.ocean_indices), dtype=int)
    gridNewRadIndex = np.zeros(len(c.grid.ocean_indices), dtype=bool)
    nSites = len(r)

    # iterate over each radial dataset (site)
    #
    for i in range(nSites):
        #
        # compute small circle based on maximum range of data, adding grid search radius, using WGS84
        #
        scLat, scLon = scircle1(r[i].sitelatitude, r[i].sitelongitude, r[i].maxrange + c.rtv('grid_search_radius'))
        #
        # find total grid points inside the small circle
        #
        in_circle = inpolygon(c.grid.ocean_xy[:, 0], c.grid.ocean_xy[:, 1], scLon, scLat)
        #
        # increment grid count for points inside radial coverage
        #
        gridAllRadCount += in_circle
        #
        # index grid points covered by new data
        #
        if r[i].isnew:
            gridNewRadIndex |= in_circle

    # define grid points with potential solutions based on new radial coverage
    # and number of sites overlapping the grid point
    #
    sPoint = np.where((gridNewRadIndex) & (gridAllRadCount >= c.rtv('min_rad_sites')))[0]

    if len(sPoint) == 0:
        logger.info('No potential total solution points found')
        return U

    nPoints = len(sPoint)
    logger.info(f'Found {nPoints} potential total solution points')

    # define grid small circle field name
    #
    if c.rtv('grid_search_radius') == int(c.rtv('grid_search_radius')):
        scircle_xfield = f"ocean_x_scircle{c.rtv('grid_search_radius')}km"
        scircle_yfield = f"ocean_y_scircle{c.rtv('grid_search_radius')}km"
    elif c.rtv('grid_search_radius') * 1000 == int(c.rtv('grid_search_radius') * 1000):
        scircle_xfield = f"ocean_x_scircle{int(c.rtv('grid_search_radius') * 1000)}m"
        scircle_yfield = f"ocean_y_scircle{int(c.rtv('grid_search_radius') * 1000)}m"
    else:
        errmsg = f"Invalid grid search radius of {c.rtv('grid_search_radius')} km. Value must be a whole number when represented in meters"
        logger.error(errmsg)
        raise ValueError('rtvproc:rtvComputeTotals:configurationError', errmsg)

    if scircle_xfield not in c.grid or scircle_yfield not in c.grid:
        errmsg = f"Grid small circle field {scircle_xfield} and/or {scircle_xfield} not found"
        logger.error(errmsg)
        raise AttributeError('rtvproc:rtvComputeTotals:missingStructField', errmsg)

    # compute total solutions
    #
    u = np.full(len(c.grid.ocean_indices), np.nan)
    v = np.full(len(c.grid.ocean_indices), np.nan)
    dopx = np.full(len(c.grid.ocean_indices), np.nan)
    dopy = np.full(len(c.grid.ocean_indices), np.nan)
    hdop = np.full(len(c.grid.ocean_indices), np.nan)
    nRads = np.zeros(len(c.grid.ocean_indices), dtype=int)
    nRadSites = np.zeros(len(c.grid.ocean_indices), dtype=int)

    # loop over each potential solution grid point
    #
    for i in range(nPoints):

        scLat = c.grid[scircle_yfield][sPoint[i]]
        scLon = c.grid[scircle_xfield][sPoint[i]]
        nSitesContributing = 0
        containsNewData = False
        rpSpeed = []
        rpHeading = []

        # loop over each site to find radials within the grid point's search radius
        for j in range(nSites):

            in_circle = inpolygon(r[j].longitude, r[j].latitude, scLon, scLat)

            if np.any(in_circle):
                rpSpeed.extend(r[j].speed[in_circle])
                rpHeading.extend(r[j].heading[in_circle])
                nSitesContributing += 1
                
                if not containsNewData and r[j].isnew:
                    containsNewData = True

        # see if we have (1) new radial data with (2) enough contributing sites and (3) enough radials to compute a total
        if containsNewData and nSitesContributing >= c.rtv('min_rad_sites') and len(rpSpeed) >= c.rtv('min_radials'):
            u[sPoint[i]], v[sPoint[i]], dopx[sPoint[i]], dopy[sPoint[i]], hdop[sPoint[i]] = uwlsTotal(rpSpeed, rpHeading)
            nRads[sPoint[i]] = len(rpSpeed)
            nRadSites[sPoint[i]] = nSitesContributing

    if np.any(nRads):
        logger.debug(f"Computed {np.sum(np.isfinite(u))} new total solutions (pre-filter)")
    else:
        logger.info('No new solutions computed')
        return U

    # filter total solutions
    #
    iInf = np.isinf(u) | np.isinf(v)  # infinite solutions
    iCpx = np.imag(u) > 0 | np.imag(v) > 0 | np.imag(dopx) > 0 | np.imag(dopy) > 0  # complex solutions
    iSpd = np.sqrt(u ** 2 + v ** 2) > c.rtv('max_rtv_speed')  # speed threshold
    iHdop = hdop > c.rtv('uwls_max_hdop')  # HDOP threshold
    mask = iInf | iCpx | iSpd | iHdop

    u[mask] = np.nan
    v[mask] = np.nan
    dopx[mask] = np.nan
    dopy[mask] = np.nan
    hdop[mask] = np.nan
    nRads[mask] = 0
    nRadSites[mask] = 0

    if np.any(mask):
        logger.info(f"Masked {np.sum(mask)} total solutions; {np.sum(iInf)} inf, {np.sum(iCpx)} complex, {np.sum(iSpd)} speed, {np.sum(iHdop)} hdop")
    else:
        logger.debug('No solutions eliminated by masking')

    # structure data
    #
    if np.any(nRads):
        U['lat'] = c.grid.ocean_xy[:, 1]
        U['lon'] = c.grid.ocean_xy[:, 0]
        U['u'] = u
        U['v'] = v
        U['dopx'] = dopx
        U['dopy'] = dopy
        U['hdop'] = hdop
        U['nRads'] = nRads
        U['nSites'] = nRadSites
        U['grid'] = {
            'resolution_km': c.grid.resolution_km,
            'projection': c.grid.projection,
            'x_range': c.grid.x_range,
            'y_range': c.grid.y_range,
            'dx': c.grid.dx,
            'dy': c.grid.dy,
            'size': c.grid.size,
            'ocean_indices': c.grid.ocean_indices
        }
        logger.info(f"Computed {np.sum(np.isfinite(u))} new total solutions")
    else:
        logger.info('No new solutions computed')

    return U


# . .. . ... . . .. . ... . . .. . ... . . .. . ... . . .. . ... . . .. . ... . . .. . ... .
# Compute a small circle on a sphere or ellipsoid.
#
#   lat0,lon0 = geodetic latitude, longitude of center of small circle (degrees)
#   radius    = radius of circle (kilometers)
#   npts      = number of points to compute (None computes 360 points)
#   ellipsoid = Ellipsoid definition (None assumes a sphere)
#
#   returns lats,lons where lats,lons are vectors of geodetic
#           latitudes,longitudes comprising the small circle.
#
#
def scircle1(lat0, lon0, radius, npts=None, ellipsoid=None):

    if npts is None:
        npts = 360

    lat0 = np.radians(lat0)
    lon0 = np.radians(lon0)

    if ellipsoid is None:
        ellipsoid = [1.0, 1.0]

    delaz = 2 * np.pi / npts
    az = np.linspace(0, 2 * np.pi - delaz, npts)

    lats = np.zeros(npts)
    lons = np.zeros(npts)

    for i in range(npts):
        lats[i], lons[i] = scircle(lat0, lon0, az[i], radius, ellipsoid)

    return lats, lons


# . .. . ... . . .. . ... . . .. . ... . . .. . ... . . .. . ... . . .. . ... . . .. . ... .
# Compute a single point on a small circle on a sphere or ellipsoid.
#
#   lat0, lon0 = geodetic latitude and longitude of center of small circle (radians)
#   az         = azimuth of point on small circle (radians)
#   radius     = radius of circle (kilometers)
#   ellipsoid  = Ellipsoid definition (a, e) where:
#   a          = equatorial radius of ellipsoid (kilometers)
#   e          = eccentricity of ellipsoid
#
#   returns lat,lon where lat,lon are the geodetic latitude and longitude
#           of the point on the small circle (radians).
#
#
def scircle(lat0, lon0, az, radius, ellipsoid):

    a, e = ellipsoid

    r = radius / a
    lat = np.arcsin(np.sin(lat0) * np.cos(r) + np.cos(lat0) * np.sin(r) * np.cos(az))
    lon = lon0 + np.arctan2(np.sin(az) * np.sin(r) * np.cos(lat0), np.cos(r) - np.sin(lat0) * np.sin(lat))

    return lat, lon


# . .. . ... . . .. . ... . . .. . ... . . .. . ... . . .. . ... . . .. . ... . . .. . ... .
# Determine if a set of points are inside a polygon.
#
#    xq, yq = coordinates of points to test (scalars or arrays)
#    xv, yv = coordinates of vertices of polygon
#
#    Returns a boolean array with True if the corresponding point is
#    inside the polygon.
#
#
def inpolygon(xq, yq, xv, yv):

    nv = len(xv)
    xq = np.atleast_1d(xq)
    yq = np.atleast_1d(yq)

    inside = np.zeros(len(xq), dtype=bool)

    for i in range(len(xq)):
    
        xpoly = np.hstack((xv, xv[0]))
        ypoly = np.hstack((yv, yv[0]))

        j = np.nonzero(((ypoly[:-1] <= yq[i]) & (ypoly[1:] > yq[i])) |
                       ((ypoly[:-1] > yq[i]) & (ypoly[1:] <= yq[i])))[0]

        if len(j) > 0:
            x = xpoly[j]
            y = ypoly[j]
            x = x + (yq[i] - y) / (ypoly[j + 1] - ypoly[j]) * (xpoly[j + 1] - xpoly[j])
            nxor = np.sum(x < xq[i])
            inside[i] = nxor % 2 == 1

    return inside


# . .. . ... . . .. . ... . . .. . ... . . .. . ... . . .. . ... . . .. . ... . . .. . ... .
# Unweighted least-squares solution for total vector from radial data.
#
#   speed   = Radial speeds (cm/s)
#   heading = Radial bearings (degrees clockwise from north)
#
#   returns u, v, dopx, dopy, hdop where:
#      u,v       = E,N components of total vector (cm/s)
#      dopx,dopy = X,Y dilution of precision
#      hdop      = Horizontal dilution of precision
#
#
def uwlsTotal(speed, heading):

    speed = np.array(speed)
    heading = np.array(heading)
    #
    # convert to radians
    #
    theta = np.radians(90 - heading)
    #
    # construct design matrix
    #
    A = np.column_stack((np.cos(theta), np.sin(theta)))
    #
    # least-squares solution
    #
    x, _, _, _ = np.linalg.lstsq(A, speed, rcond=None)

    u, v = x
    #
    # compute DOP
    #
    Q = np.linalg.inv(A.T @ A)
    dopx = np.sqrt(Q[0, 0])
    dopy = np.sqrt(Q[1, 1])
    hdop = np.sqrt(dopx**2 + dopy**2)

    return u, v, dopx, dopy, hdop


""".. . .. ... . .. ... . .. ... . .. ... . .. ... . .. ... . .. ... . .. ... . .. ... . .. ... . .. ... . .. ... . .. ... . .. ... . .. ... . .. .

    ..code translates the provided MATLAB function `rtvComputeTotals` to Python. 
    ..computes total velocity solutions from radial velocity measurements using input processing parameters. 
    ..function takes three inputs: 
        c		 (a configuration structure), 
        logger   (a logger object)
        r		 (a radial data structure). 

    ..returns a dictionary `U` containing the total solution structure with fields such as 
    `lat`, `lon`, `u`, `v`, `dopx`, `dopy`, `hdop`, `nRads`, `nSites`, and `grid` (which is another dictionary containing grid information)

    The code follows the same logic as the MATLAB function, including initializing return values, reducing the total grid solution space, defining
    the grid small circle field name, computing total solutions, filtering total solutions, and structuring the data. It also includes helper 
    functions `scircle1`, `scircle`, `inpolygon`, and `uwlsTotal` for computing small circles, determining if points are inside a polygon, and 
    computing the unweighted least-squares solution for the total vector from radial data, respectively.

    Note that the code assumes the availability of the necessary data structures (`c` and `r`) and the `uwlsTotal` function, which is not provided 
    in the original MATLAB code.

"""