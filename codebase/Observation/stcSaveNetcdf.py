"""

    STCSAVENETCDF Saves STC data to a NetCDF file

    [ success, message ] = stcSaveNetCDF( c, logger, t, A ) saves sub-tidal
    current solutions and corresponding metadata in NetCDF format using
    the Climate and Foecast (CF) and Attribute Convention for Data
    Discovery (ACDD) metadata standards.

    The specific conventions and versions are hard-coded in this function
    as it only supports one version for each convention and there is no
    intention to provide options or support for multiple conventions or
    versions.

    The return values success and message will be true and empty,
    respectively, if there are no errors.  Otherwise, success will be
    false and any response will be provided in message.

    See also PRODUCTVERSION, NETCDF

   Developer Notes:

    Update the NetCDF format version as needed (e.g. changes to the way
    data are encoded; types, new vars, new metadata, updates in metadata
    standards, ...). Use major.minor.maintenance as indicated below.

    Note that grid needs to be oriented from NW in (1,1) to SE in (M,N)
    for proper orientation when written.  Worth noting if/when grids and
    land mask files are documented somewhere.

    The deflation parameters are hard-coded in this function. They could
    be abstracted to the configuration, since there's likely every only
    going to be a single set of parameters, it's OK to define here - at
    least for now.

   HF-Radar Network
   Scripps Institution of Oceanography
   Coastal Observing Research and Development Center

"""
import os
import textwrap
import numpy as np
import netCDF4 as nc
from datetime import datetime, timedelta


def stcSaveNetcdf(c, logger, t, A):

    # Initialize return values
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
        writeNetCDF(c, logger, t, A)
    except Exception as e:
        message = f'Error saving {c.total.ncpathfile}: {e}'
        return success, message

    success = True
    return success, message


def writeNetCDF(c, logger, t, A):

    # Define conventions & versions
    nc_format_version = '1.1.00'
    nc_conventions = {'CF': 'CF-1.7', 'ACDD': 'ACDD-1.3'}
    nc_cf_std_name_version = 'CF Standard Name Table, Version 51'

    # Define default deflation parameters
    nc_deflate = {'enable': True, 'level': 2, 'shuffle': True}

    # Format Variable Data
    u_avg = np.nan_to_num(np.rot90(np.round(A.uAvg[A.grid.ocean_indices].reshape(A.grid.size), -3), -1))
    v_avg = np.nan_to_num(np.rot90(np.round(A.vAvg[A.grid.ocean_indices].reshape(A.grid.size), -3), -1))
    u_var = np.nan_to_num(np.rot90(np.round(A.uVar[A.grid.ocean_indices].reshape(A.grid.size), -3), -1))
    v_var = np.nan_to_num(np.rot90(np.round(A.vVar[A.grid.ocean_indices].reshape(A.grid.size), -3), -1))
    u_min = np.nan_to_num(np.rot90(np.round(A.uMin[A.grid.ocean_indices].reshape(A.grid.size), -3), -1))
    v_min = np.nan_to_num(np.rot90(np.round(A.vMin[A.grid.ocean_indices].reshape(A.grid.size), -3), -1))
    u_max = np.nan_to_num(np.rot90(np.round(A.uMax[A.grid.ocean_indices].reshape(A.grid.size), -3), -1))
    v_max = np.nan_to_num(np.rot90(np.round(A.vMax[A.grid.ocean_indices].reshape(A.grid.size), -3), -1))
    n_obs = np.nan_to_num(np.rot90(np.round(A.nGood[A.grid.ocean_indices].reshape(A.grid.size), -3), -1))

    # Replace NaN with fill values
    fill_value = nc.default_fillvals['short']
    u_avg[np.isnan(u_avg)] = fill_value
    v_avg[np.isnan(v_avg)] = fill_value
    u_var[np.isnan(u_var)] = fill_value
    v_var[np.isnan(v_var)] = fill_value
    u_min[np.isnan(u_min)] = fill_value
    v_min[np.isnan(v_min)] = fill_value
    u_max[np.isnan(u_max)] = fill_value
    v_max[np.isnan(v_max)] = fill_value
    n_obs[np.isnan(n_obs)] = fill_value

    # History
    logger.notice('Writing values to file')

    # Open NetCDF file
    mode = nc.NC_NETCDF4 | nc.NC_CLASSIC_MODEL
    ncid = nc.Dataset(c.total.ncpathfile, mode=mode)

    # Define Dimensions
    dimid_t = ncid.createDimension('time', None)
    dimid_lat = ncid.createDimension('lat', A.grid.size[0])
    dimid_lon = ncid.createDimension('lon', A.grid.size[1])
    dimid_nv = ncid.createDimension('nv', 2)

    # Define Coordinate Variables & Add Attributes
    varid_t = ncid.createVariable('time', 'i4', ('time',))
    varid_t.setncattr('standard_name', 'time')
    varid_t.setncattr('units', 'seconds since 1970-01-01')
    varid_t.setncattr('calendar', 'gregorian')
    varid_t.setncattr('bounds', 'time_bnds')
    varid_t.set_fill_off()

    varid_lat = ncid.createVariable('lat', 'f4', ('lat',))
    varid_lat.setncattr('standard_name', 'latitude')
    varid_lat.setncattr('units', 'degrees_north')

    varid_lon = ncid.createVariable('lon', 'f4', ('lon',))
    varid_lon.setncattr('standard_name', 'longitude')
    varid_lon.setncattr('units', 'degrees_east')

    # Add Global Attributes
    varid_global = ncid.getncattr('global')

    ncid.setncattr('Conventions', ','.join(nc_conventions.values()))
    ncid.setncattr('id', c.ncid(c, t))
    ncid.setncattr('date_created', datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'))
    ncid.setncattr('source', c.metadata['source'])
    if 'program' in c.metadata:
        ncid.setncattr('program', c.metadata['program'])
    if 'project' in c.metadata:
        ncid.setncattr('project', c.metadata['project'])
    ncid.setncattr('title', c.metadata['title'])
    ncid.setncattr('summary', '\n'.join(textwrap.wrap(c.metadata['summary'], 70)))
    ncid.setncattr('instrument', '\n'.join(textwrap.wrap(c.metadata['instrument'], 70)))
    ncid.setncattr('keywords', '\n'.join(textwrap.wrap(c.metadata['keywords'], 70)))
    ncid.setncattr('geospatial_lat_min', A.grid.y_range[0])
    ncid.setncattr('geospatial_lat_max', A.grid.y_range[1])
    ncid.setncattr('geospatial_lon_min', A.grid.x_range[0])
    ncid.setncattr('geospatial_lon_max', A.grid.x_range[1])
    ncid.setncattr('processing_level', '\n'.join(textwrap.wrap(c.metadata['processing_level'], 70)))

    if hasattr(A, 'history') and len(A.history) > 0:
        ncHistory = []
        for i in range(len(A.history)):
            ncHistory.append(f'{A.history[i].timestamp} {A.history[i].user} {A.history[i].program}: {A.history[i].message}')
        ncid.setncattr('history', '\n'.join(ncHistory))

    if 'references' in c.metadata:
        ncid.setncattr('references', '\n'.join(textwrap.wrap(c.metadata['references'], 70)))
    ncid.setncattr('institution', c.metadata['institution'])
    ncid.setncattr('creator_type', c.metadata['creator_type'])
    ncid.setncattr('creator_name', c.metadata['creator_name'])
    ncid.setncattr('creator_email', c.metadata['creator_email'])
    ncid.setncattr('creator_url', c.metadata['creator_url'])
    ncid.setncattr('naming_authority', c.metadata['naming_authority'])
    ncid.setncattr('standard_name_vocabulary', nc_cf_std_name_version)
    ncid.setncattr('keywords_vocabulary', c.metadata['keywords_vocabulary'])
    ncid.setncattr('instrument_vocabulary', c.metadata['instrument_vocabulary'])
    ncid.setncattr('format_version', nc_format_version)
    ncid.setncattr('product_version', productVersion(c.process))

    # Define Data Variables & Add Attributes
    varid_time_bnds = ncid.createVariable('time_bnds', 'i4', ('nv', 'time'))
    varid_time_bnds.set_fill_off()

    varid_z = ncid.createVariable('depth', 'f4', ())
    varid_z.setncattr('standard_name', 'depth')
    varid_z.setncattr('units', 'm')
    varid_z.setncattr('bounds', 'depth_bnds')
    varid_z.setncattr('comment', '\n'.join(textwrap.wrap(f'Nominal depth (and corresponding bounds) based on contributing radars', 70)))

    varid_z_bnds = ncid.createVariable('depth_bnds', 'f4', ('nv',))

    varid_wgs84 = ncid.createVariable('wgs84', 'b', ())
    varid_wgs84.setncattr('grid_mapping_name', 'latitude_longitude')
    varid_wgs84.setncattr('longitude_of_prime_meridian', 0.0)
    varid_wgs84.setncattr('semi_major_axis', 6378137.0)
    varid_wgs84.setncattr('inverse_flattening', 298.257223563)

    varid_u_avg = ncid.createVariable('u_mean', 's2', ('lon', 'lat', 'time'))
    varid_u_avg.set_fill_off()
    if c.domain == "glna":
        varid_u_avg.setncattr('long_name', 'mean eastward surface velocity')
    else:
        varid_u_avg.setncattr('standard_name', 'surface_eastward_sea_water_velocity')
        varid_u_avg.setncattr('long_name', 'mean eastward surface velocity')
    varid_u_avg.setncattr('units', 'm s-1')
    varid_u_avg.setncattr('scale_factor', 0.01)
    varid_u_avg.setncattr('grid_mapping', 'wgs84')
    varid_u_avg.setncattr('coordinates', 'depth')
    varid_u_avg.setncattr('cell_methods', 'depth: mean time: mean (interval: 1 hour comment: 1 hour average)')
    varid_u_avg.setncattr('ancillary_variables', 'n_obs')

    varid_v_avg = ncid.createVariable('v_mean', 's2', ('lon', 'lat', 'time'))
    varid_v_avg.set_fill_off()
    if c.domain == "glna":
        varid_v_avg.setncattr('long_name', 'mean northward surface velocity')
    else:
        varid_v_avg.setncattr('standard_name', 'surface_northward_sea_water_velocity')
        varid_v_avg.setncattr('long_name', 'mean northward surface velocity')
    varid_v_avg.setncattr('units', 'm s-1')
    varid_v_avg.setncattr('scale_factor', 0.01)
    varid_v_avg.setncattr('grid_mapping', 'wgs84')
    varid_v_avg.setncattr('coordinates', 'depth')
    varid_v_avg.setncattr('cell_methods', 'depth: mean time: mean (interval: 1 hour comment: 1 hour average)')
    varid_v_avg.setncattr('ancillary_variables', 'n_obs')

    varid_u_var = ncid.createVariable('u_var', 's2', ('lon', 'lat', 'time'))
    varid_u_var.set_fill_off()
    if c.domain == "glna":
        varid_u_var.setncattr('long_name', 'eastward surface velocity variance')
    else:
        varid_u_var.setncattr('standard_name', 'surface_eastward_sea_water_velocity')
        varid_u_var.setncattr('long_name', 'eastward surface velocity variance')
    varid_u_var.setncattr('units', 'm2 s-2')
    varid_u_var.setncattr('scale_factor', 0.0001)
    varid_u_var.setncattr('grid_mapping', 'wgs84')
    varid_u_var.setncattr('coordinates', 'depth')
    varid_u_var.setncattr('cell_methods', 'depth: mean time: variance (interval: 1 hour comment: 1 hour average)')
    varid_u_var.setncattr('ancillary_variables', 'n_obs')

    varid_v_var = ncid.createVariable('v_var', 's2', ('lon', 'lat', 'time'))
    varid_v_var.set_fill_off()
    if c.domain == "glna":
        varid_v_var.setncattr('long_name', 'northward surface velocity variance')
    else:
        varid_v_var.setncattr('standard_name', 'surface_northward_sea_water_velocity')
        varid_v_var.setncattr('long_name', 'northward surface velocity variance')
    varid_v_var.setncattr('units', 'm2 s-2')
    varid_v_var.setncattr('scale_factor', 0.0001)
    varid_v_var.setncattr('grid_mapping', 'wgs84')
    varid_v_var.setncattr('coordinates', 'depth')
    varid_v_var.setncattr('cell_methods', 'depth: mean time: variance (interval: 1 hour comment: 1 hour average)')
    varid_v_var.setncattr('ancillary_variables', 'n_obs')

    varid_u_min = ncid.createVariable('u_min', 's2', ('lon', 'lat', 'time'))
    varid_u_min.set_fill_off()
    if c.domain == "glna":
        varid_u_min.setncattr('long_name', 'minimum eastward surface velocity')
    else:
        varid_u_min.setncattr('standard_name', 'surface_eastward_sea_water_velocity')
        varid_u_min.setncattr('long_name', 'minimum eastward surface velocity')
    varid_u_min.setncattr('units', 'm s-1')
    varid_u_min.setncattr('scale_factor', 0.01)
    varid_u_min.setncattr('grid_mapping', 'wgs84')
    varid_u_min.setncattr('coordinates', 'depth')
    varid_u_min.setncattr('cell_methods', 'depth: mean time: minimum (interval: 1 hour comment: 1 hour average)')
    varid_u_min.setncattr('ancillary_variables', 'n_obs')

    varid_v_min = ncid.createVariable('v_min', 's2', ('lon', 'lat', 'time'))
    varid_v_min.set_fill_off()
    if c.domain == "glna":
        varid_v_min.setncattr('long_name', 'minimum northward surface velocity')
    else:
        varid_v_min.setncattr('standard_name', 'surface_northward_sea_water_velocity')
        varid_v_min.setncattr('long_name', 'minimum northward surface velocity')
    varid_v_min.setncattr('units', 'm s-1')
    varid_v_min.setncattr('scale_factor', 0.01)
    varid_v_min.setncattr('grid_mapping', 'wgs84')
    varid_v_min.setncattr('coordinates', 'depth')
    varid_v_min.setncattr('cell_methods', 'depth: mean time: minimum (interval: 1 hour comment: 1 hour average)')
    varid_v_min.setncattr('ancillary_variables', 'n_obs')

    varid_u_max = ncid.createVariable('u_max', 's2', ('lon', 'lat', 'time'))
    varid_u_max.set_fill_off()
    if c.domain == "glna":
        varid_u_max.setncattr('long_name', 'maximum eastward surface velocity')
    else:
        varid_u_max.setncattr('standard_name', 'surface_eastward_sea_water_velocity')
        varid_u_max.setncattr('long_name', 'maximum eastward surface velocity')
    varid_u_max.setncattr('units', 'm s-1')
    varid_u_max.setncattr('scale_factor', 0.01)
    varid_u_max.setncattr('grid_mapping', 'wgs84')
    varid_u_max.setncattr('coordinates', 'depth')
    varid_u_max.setncattr('cell_methods', 'depth: mean time: maximum (interval: 1 hour comment: 1 hour average)')
    varid_u_max.setncattr('ancillary_variables', 'n_obs')

    varid_v_max = ncid.createVariable('v_max', 's2', ('lon', 'lat', 'time'))
    varid_v_max.set_fill_off()
    if c.domain == "glna":
        varid_v_max.setncattr('long_name', 'maximum northward surface velocity')
    else:
        varid_v_max.setncattr('standard_name', 'surface_northward_sea_water_velocity')
        varid_v_max.setncattr('long_name', 'maximum northward surface velocity')
    varid_v_max.setncattr('units', 'm s-1')
    varid_v_max.setncattr('scale_factor', 0.01)
    varid_v_max.setncattr('grid_mapping', 'wgs84')
    varid_v_max.setncattr('coordinates', 'depth')
    varid_v_max.setncattr('cell_methods', 'depth: mean time: maximum (interval: 1 hour comment: 1 hour average)')
    varid_v_max.setncattr('ancillary_variables', 'n_obs')

    varid_n_obs = ncid.createVariable('n_obs', 's2', ('lon', 'lat', 'time'))
    varid_n_obs.set_fill_off()
    varid_n_obs.setncattr('standard_name', 'number_of_observations')
    varid_n_obs.setncattr('units', 'count')
    varid_n_obs.setncattr('grid_mapping', 'wgs84')
    varid_n_obs.setncattr('coordinates', 'depth')
    varid_n_obs.setncattr('cell_methods', 'time: sum (interval: 1 hour)')

    # Exit Definition Mode
    ncid.sync()

    # Add Data Values
    varid_lat[:] = np.arange(A.grid.y_range[0], A.grid.y_range[1] + A.grid.dy, A.grid.dy)
    varid_lon[:] = np.arange(A.grid.x_range[0], A.grid.x_range[1] + A.grid.dx, A.grid.dx)
    varid_t[:] = np.array([0])
    varid_time_bnds[:] = np.array([t - timedelta(hours=12.5), t + timedelta(hours=12.5)])
    varid_z[:] = c.metadata['depth_mean']
    varid_z_bnds[:] = np.array([0, c.metadata['depth_bottom']])
    varid_u_avg[:] = u_avg
    varid_v_avg[:] = v_avg
    varid_u_var[:] = u_var
    varid_v_var[:] = v_var
    varid_u_min[:] = u_min
    varid_v_min[:] = v_min
    varid_u_max[:] = u_max
    varid_v_max[:] = v_max
    varid_n_obs[:] = n_obs

    # Close file
    ncid.close()


def productVersion(process):
    # Implement productVersion function here
    pass
