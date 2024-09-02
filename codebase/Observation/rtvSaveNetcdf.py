"""

    rtvSaveNetcdf.py



    HF-Radar Network
    Scripps Institution of Oceanography
    Coastal Observing Research and Development Center

"""
import os
import numpy as np
import netCDF4 as nc
from datetime import datetime, timedelta


def rtvSaveNetcdf(c, t, U, r):
    success = False
    message = ''

    # Check save directory exists
    if not os.path.isdir(c.total.ncdir):
        try:
            os.makedirs(c.total.ncdir)
        except OSError as err:
            message = f'Failed to make dir {c.total.ncdir}: {err}'
            return success, message

    # Save
    try:
        writeNetCDF(c, t, U, r)
    except Exception as e:
        message = f'Error saving {c.total.ncpathfile}: {e}'
        return success, message

    success = True
    return success, message


def writeNetCDF(c, t, U, r):
    # Define conventions & versions
    nc_format_version = '1.1.00'
    nc_conventions = {'CF': 'CF-1.7', 'ACDD': 'ACDD-1.3'}
    nc_cf_std_name_version = 'CF Standard Name Table, Version 51'

    # Define default deflation parameters
    nc_deflate = {'enable': True, 'level': 2, 'shuffle': True}

    # Format Variable Data
    u = np.full(U.grid.size, np.nan)
    u[U.grid.ocean_indices] = U.u
    u = np.rot90(u, k=-1)
    u = np.round(u)  # 1 cm/s accuracy

    v = np.full(U.grid.size, np.nan)
    v[U.grid.ocean_indices] = U.v
    v = np.rot90(v, k=-1)
    v = np.round(v)  # 1 cm/s accuracy

    dopx = np.full(U.grid.size, np.nan)
    dopx[U.grid.ocean_indices] = U.dopx
    dopx = np.rot90(dopx, k=-1)
    dopx = np.round(dopx * 100)  # Scale to store as short; accuracy to 100ths

    dopy = np.full(U.grid.size, np.nan)
    dopy[U.grid.ocean_indices] = U.dopy
    dopy = np.rot90(dopy, k=-1)
    dopy = np.round(dopy * 100)  # Scale to store as short; accuracy to 100ths

    hdop = np.full(U.grid.size, np.nan)
    hdop[U.grid.ocean_indices] = U.hdop
    hdop = np.rot90(hdop, k=-1)
    hdop = np.round(hdop * 100)  # Scale to store as short; accuracy to 100ths

    n_sites = np.full(U.grid.size, np.nan)
    n_sites[U.grid.ocean_indices] = U.nSites
    n_sites = np.rot90(n_sites, k=-1)

    n_rads = np.full(U.grid.size, np.nan)
    n_rads[U.grid.ocean_indices] = U.nRads
    n_rads = np.rot90(n_rads, k=-1)

    # Filter all data by HDOP
    mask = hdop >= c.rtv['uwls_max_hdop_nc'] * 100
    if np.any(mask):
        u[mask] = np.nan
        v[mask] = np.nan
        dopx[mask] = np.nan
        dopy[mask] = np.nan
        hdop[mask] = np.nan
        n_sites[mask] = np.nan
        n_rads[mask] = np.nan

    # Replace NaN with fill values
    fill_value = nc.get_default_fillvals()['short']
    u[np.isnan(u)] = fill_value
    v[np.isnan(v)] = fill_value
    dopx[np.isnan(dopx)] = fill_value
    dopy[np.isnan(dopy)] = fill_value
    hdop[np.isnan(hdop)] = fill_value
    n_sites[np.isnan(n_sites)] = nc.get_default_fillvals()['byte']
    n_rads[np.isnan(n_rads)] = fill_value

    # Open NetCDF file
    mode = nc.NC_NETCDF4 | nc.NC_CLASSIC_MODEL
    ncid = nc.Dataset(c.total.ncpathfile, mode=mode)

    # Define Dimensions
    dimid_t = ncid.createDimension('time', None)
    dimid_lat = ncid.createDimension('lat', U.grid.size[0])
    dimid_lon = ncid.createDimension('lon', U.grid.size[1])
    dimid_nv = ncid.createDimension('nv', 2)

    # Define Coordinate Variables & Add Attributes
    varid_t = ncid.createVariable('time', 'i4', ('time',))
    varid_t.standard_name = 'time'
    varid_t.units = 'seconds since 1970-01-01'
    varid_t.calendar = 'gregorian'
    varid_t.bounds = 'time_bnds'

    varid_lat = ncid.createVariable('lat', 'f4', ('lat',))
    varid_lat.standard_name = 'latitude'
    varid_lat.units = 'degrees_north'

    varid_lon = ncid.createVariable('lon', 'f4', ('lon',))
    varid_lon.standard_name = 'longitude'
    varid_lon.units = 'degrees_east'

    # Add Global Attributes
    ncid.Conventions = ', '.join(nc_conventions.values())
    ncid.id = c.ncid(c, t)
    ncid.date_created = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    ncid.source = c.metadata['source']
    ncid.title = c.metadata['title']
    ncid.summary = c.metadata['summary']
    ncid.instrument = c.metadata['instrument']
    ncid.keywords = c.metadata['keywords']
    ncid.geospatial_lat_min = U.grid.y_range[0]
    ncid.geospatial_lat_max = U.grid.y_range[1]
    ncid.geospatial_lon_min = U.grid.x_range[0]
    ncid.geospatial_lon_max = U.grid.x_range[1]
    ncid.processing_level = c.metadata['processing_level']
    ncid.history = ''
    ncid.references = c.metadata.get('references', '')
    ncid.institution = c.metadata['institution']
    ncid.creator_type = c.metadata['creator_type']
    ncid.creator_name = c.metadata['creator_name']
    ncid.creator_email = c.metadata['creator_email']
    ncid.creator_url = c.metadata['creator_url']
    ncid.naming_authority = c.metadata['naming_authority']
    ncid.standard_name_vocabulary = nc_cf_std_name_version
    ncid.keywords_vocabulary = c.metadata['keywords_vocabulary']
    ncid.instrument_vocabulary = c.metadata['instrument_vocabulary']
    ncid.format_version = nc_format_version
    ncid.product_version = nc.productVersion(c.process)

    # Define Data Variables & Add Attributes
    varid_time_bnds = ncid.createVariable('time_bnds', 'i4', ('nv', 'time'))

    varid_z = ncid.createVariable('depth', 'f4', ())
    varid_z.standard_name = 'depth'
    varid_z.units = 'm'
    varid_z.bounds = 'depth_bnds'
    varid_z.comment = 'Nominal depth (and corresponding bounds) based on contributing radars'

    varid_z_bnds = ncid.createVariable('depth_bnds', 'f4', ('nv',))

    varid_wgs84 = ncid.createVariable('wgs84', 'b', ())
    varid_wgs84.grid_mapping_name = 'latitude_longitude'
    varid_wgs84.longitude_of_prime_meridian = 0.0
    varid_wgs84.semi_major_axis = 6378137.0
    varid_wgs84.inverse_flattening = 298.257223563

    varid_u = ncid.createVariable('u', 's2', ('lon', 'lat', 'time'))
    varid_u.long_name = 'surface eastward water velocity' if c.domain == 'glna' else 'surface_eastward_sea_water_velocity'
    varid_u.units = 'm s-1'
    varid_u.scale_factor = 0.01
    varid_u.grid_mapping = 'wgs84'
    varid_u.coordinates = 'depth'
    varid_u.cell_methods = 'depth: mean time: mean'
    varid_u.ancillary_variables = 'dopx'

    varid_v = ncid.createVariable('v', 's2', ('lon', 'lat', 'time'))
    varid_v.long_name = 'surface northward water velocity' if c.domain == 'glna' else 'surface_northward_sea_water_velocity'
    varid_v.units = 'm s-1'
    varid_v.scale_factor = 0.01
    varid_v.grid_mapping = 'wgs84'
    varid_v.coordinates = 'depth'
    varid_v.cell_methods = 'depth: mean time: mean'
    varid_v.ancillary_variables = 'dopy'

    # Add Data Values
    ncid.variables['lat'][:] = np.arange(U.grid.size[0]) * U.grid.dy + U.grid.y_range[0]
    ncid.variables['lon'][:] = np.arange(U.grid.size[1]) * U.grid.dx + U.grid.x_range[0]
    ncid.variables['time'][:] = np.arange(len(t))
    ncid.variables['time_bnds'][:] = np.array([[t[i] - timedelta(minutes=30), t[i] + timedelta(minutes=30)] for i in range(len(t))]).flatten()
    ncid.variables['depth'][:] = c.metadata['depth_mean']
    ncid.variables['depth_bnds'][:] = [0, c.metadata['depth_bottom']]
    ncid.variables['u'][:] = u.flatten()
    ncid.variables['v'][:] = v.flatten()
    ncid.variables['dopx'][:] = dopx.flatten()
    ncid.variables['dopy'][:] = dopy.flatten()
    ncid.variables['hdop'][:] = hdop.flatten()
    ncid.variables['number_of_sites'][:] = n_sites.flatten()
    ncid.variables['number_of_radials'][:] = n_rads.flatten()

    # Close file
    ncid.close()
