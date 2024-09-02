"""

   ltaSaveNetcdf.py

        [ success, message ] = ltaSaveNetCDF( c, t, A ) saves long-term

    average solutions and corresponding metadata in NetCDF format using
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
import numpy as np
import netCDF4 as nc
import productVersion
from datetime import datetime, timedelta


def ltaSaveNetcdf(c, t, A):

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
        writeNetCDF(c, t, A)
    except Exception as e:
        message = f'Error saving {c.total.ncpathfile}: {e}'
        return success, message

    success = True
    return success, message


def writeNetCDF(c, t, A):
    # Define conventions & versions
    nc.set_default_fill(nc.FILL_SHORT)
    nc.set_default_format('NETCDF4')

    nc_file = nc.Dataset(c.total.ncpathfile, 'w', format='NETCDF4')

    # Define default deflation parameters
    nc_file.deflate_level = 2
    nc_file.deflate_shuffle = True

    # Define subprocess specific parameters
    if c.subprocess['name'] == 'month':
        min_temporal_coverage = c.lta['min_month_temporal_coverage']
        time_bnds = np.array([t - timedelta(days=1), t + timedelta(days=1)])
    elif c.subprocess['name'] == 'year':
        min_temporal_coverage = c.lta['min_year_temporal_coverage']
        time_bnds = np.array([t.replace(month=1, day=1) - timedelta(days=1),
                              t.replace(month=1, day=1) + timedelta(days=1)])

    # Format Variable Data
    u_avg = np.nan_to_num(np.round(np.rot90(A.uAvg[A.grid.ocean_indices], -1), 0))
    v_avg = np.nan_to_num(np.round(np.rot90(A.vAvg[A.grid.ocean_indices], -1), 0))
    u_var = np.nan_to_num(np.round(np.rot90(A.uVar[A.grid.ocean_indices], -1), 0))
    v_var = np.nan_to_num(np.round(np.rot90(A.vVar[A.grid.ocean_indices], -1), 0))
    u_min = np.nan_to_num(np.round(np.rot90(A.uMin[A.grid.ocean_indices], -1), 0))
    v_min = np.nan_to_num(np.round(np.rot90(A.vMin[A.grid.ocean_indices], -1), 0))
    u_max = np.nan_to_num(np.round(np.rot90(A.uMax[A.grid.ocean_indices], -1), 0))
    v_max = np.nan_to_num(np.round(np.rot90(A.vMax[A.grid.ocean_indices], -1), 0))
    n_obs = np.nan_to_num(np.rot90(A.nGood[A.grid.ocean_indices], -1))

    # Define Dimensions
    dim_time = nc_file.createDimension('time', None)
    dim_lat = nc_file.createDimension('lat', A.grid.size[0])
    dim_lon = nc_file.createDimension('lon', A.grid.size[1])
    dim_nv = nc_file.createDimension('nv', 2)

    # Define Coordinate Variables & Add Attributes
    var_time = nc_file.createVariable('time', 'i4', ('time',))
    var_time.standard_name = 'time'
    var_time.units = 'seconds since 1970-01-01'
    var_time.calendar = 'gregorian'
    var_time.bounds = 'time_bnds'

    var_lat = nc_file.createVariable('lat', 'f4', ('lat',))
    var_lat.standard_name = 'latitude'
    var_lat.units = 'degrees_north'

    var_lon = nc_file.createVariable('lon', 'f4', ('lon',))
    var_lon.standard_name = 'longitude'
    var_lon.units = 'degrees_east'

    # Add Global Attributes
    nc_file.Conventions = 'CF-1.7, ACDD-1.3'
    nc_file.id = c.ncid(c, t)
    nc_file.date_created = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    nc_file.source = c.metadata['source']
    nc_file.program = c.metadata.get('program', '')
    nc_file.project = c.metadata.get('project', '')
    nc_file.title = c.metadata['title']
    nc_file.summary = c.metadata['summary']
    nc_file.instrument = c.metadata['instrument']
    nc_file.keywords = c.metadata['keywords']
    nc_file.geospatial_lat_min = A.grid.y_range[0]
    nc_file.geospatial_lat_max = A.grid.y_range[1]
    nc_file.geospatial_lon_min = A.grid.x_range[0]
    nc_file.geospatial_lon_max = A.grid.x_range[1]
    nc_file.processing_level = c.metadata['processing_level']
    nc_file.history = 'Writing values to file'
    nc_file.references = c.metadata.get('references', '')
    nc_file.institution = c.metadata['institution']
    nc_file.creator_type = c.metadata['creator_type']
    nc_file.creator_name = c.metadata['creator_name']
    nc_file.creator_email = c.metadata['creator_email']
    nc_file.creator_url = c.metadata['creator_url']
    nc_file.naming_authority = c.metadata['naming_authority']
    nc_file.standard_name_vocabulary = 'CF Standard Name Table, Version 51'
    nc_file.keywords_vocabulary = c.metadata['keywords_vocabulary']
    nc_file.instrument_vocabulary = c.metadata['instrument_vocabulary']
    nc_file.format_version = '1.1.00'
    nc_file.product_version = productVersion(c.process)

    # Define Data Variables & Add Attributes
    var_time_bnds = nc_file.createVariable('time_bnds', 'i4', ('nv', 'time'))

    var_z = nc_file.createVariable('depth', 'f4', ())
    var_z.standard_name = 'depth'
    var_z.units = 'm'
    var_z.bounds = 'depth_bnds'
    var_z.comment = 'Nominal depth (and corresponding bounds) based on contributing radars'

    var_z_bnds = nc_file.createVariable('depth_bnds', 'f4', ('nv',))

    var_u_avg = nc_file.createVariable('u_mean', 'i2', ('lon', 'lat', 'time'))
    var_u_avg.standard_name = 'surface_eastward_sea_water_velocity'
    var_u_avg.long_name = 'mean eastward surface velocity'
    var_u_avg.units = 'm s-1'
    var_u_avg.scale_factor = 0.01
    var_u_avg.grid_mapping = 'wgs84'
    var_u_avg.coordinates = 'depth'
    var_u_avg.cell_methods = 'depth: mean time: mean (interval: 1 hour comment: 1 hour average)'
    var_u_avg.ancillary_variables = 'n_obs'

    var_v_avg = nc_file.createVariable('v_mean', 'i2', ('lon', 'lat', 'time'))
    var_v_avg.standard_name = 'surface_northward_sea_water_velocity'
    var_v_avg.long_name = 'mean northward surface velocity'
    var_v_avg.units = 'm s-1'
    var_v_avg.scale_factor = 0.01
    var_v_avg.grid_mapping = 'wgs84'
    var_v_avg.coordinates = 'depth'
    var_v_avg.cell_methods = 'depth: mean time: mean (interval: 1 hour comment: 1 hour average)'
    var_v_avg.ancillary_variables = 'n_obs'

    var_u_var = nc_file.createVariable('u_var', 'i2', ('lon', 'lat', 'time'))
    var_u_var.standard_name = 'surface_eastward_sea_water_velocity'
    var_u_var.long_name = 'eastward surface velocity variance'
    var_u_var.units = 'm2 s-2'
    var_u_var.scale_factor = 0.0001
    var_u_var.grid_mapping = 'wgs84'
    var_u_var.coordinates = 'depth'
    var_u_var.cell_methods = 'depth: mean time: variance (interval: 1 hour comment: 1 hour average)'
    var_u_var.ancillary_variables = 'n_obs'

    var_v_var = nc_file.createVariable('v_var', 'i2', ('lon', 'lat', 'time'))
    var_v_var.standard_name = 'surface_northward_sea_water_velocity'
    var_v_var.long_name = 'northward surface velocity variance'
    var_v_var.units = 'm2 s-2'
    var_v_var.scale_factor = 0.0001
    var_v_var.grid_mapping = 'wgs84'
    var_v_var.coordinates = 'depth'
    var_v_var.cell_methods = 'depth: mean time: variance (interval: 1 hour comment: 1 hour average)'
    var_v_var.ancillary_variables = 'n_obs'

    var_u_min = nc_file.createVariable('u_min', 'i2', ('lon', 'lat', 'time'))
    var_u_min.standard_name = 'surface_eastward_sea_water_velocity'
    var_u_min.long_name = 'minimum eastward surface velocity'
    var_u_min.units = 'm s-1'
    var_u_min.scale_factor = 0.01
    var_u_min.grid_mapping = 'wgs84'
    var_u_min.coordinates = 'depth'
    var_u_min.cell_methods = 'depth: mean time: minimum (interval: 1 hour comment: 1 hour average)'
    var_u_min.ancillary_variables = 'n_obs'

    var_v_min = nc_file.createVariable('v_min', 'i2', ('lon', 'lat', 'time'))
    var_v_min.standard_name = 'surface_northward_sea_water_velocity'
    var_v_min.long_name = 'minimum northward surface velocity'
    var_v_min.units = 'm s-1'
    var_v_min.scale_factor = 0.01
    var_v_min.grid_mapping = 'wgs84'
    var_v_min.coordinates = 'depth'
    var_v_min.cell_methods = 'depth: mean time: minimum (interval: 1 hour comment: 1 hour average)'
    var_v_min.ancillary_variables = 'n_obs'

    var_u_max = nc_file.createVariable('u_max', 'i2', ('lon', 'lat', 'time'))
    var_u_max.standard_name = 'surface_eastward_sea_water_velocity'
    var_u_max.long_name = 'maximum eastward surface velocity'
    var_u_max.units = 'm s-1'
    var_u_max.scale_factor = 0.01
    var_u_max.grid_mapping = 'wgs84'
    var_u_max.coordinates = 'depth'
    var_u_max.cell_methods = 'depth: mean time: maximum (interval: 1 hour comment: 1 hour average)'
    var_u_max.ancillary_variables = 'n_obs'

    var_v_max = nc_file.createVariable('v_max', 'i2', ('lon', 'lat', 'time'))
    var_v_max.standard_name = 'surface_northward_sea_water_velocity'
    var_v_max.long_name = 'maximum northward surface velocity'
    var_v_max.units = 'm s-1'
    var_v_max.scale_factor = 0.01
    var_v_max.grid_mapping = 'wgs84'
    var_v_max.coordinates = 'depth'
    var_v_max.cell_methods = 'depth: mean time: maximum (interval: 1 hour comment: 1 hour average)'
    var_v_max.ancillary_variables = 'n_obs'

    var_n_obs = nc_file.createVariable('n_obs', 'i2', ('lon', 'lat', 'time'))
    var_n_obs.standard_name = 'number_of_observations'
    var_n_obs.units = 'count'
    var_n_obs.grid_mapping = 'wgs84'
    var_n_obs.coordinates = 'depth'
    var_n_obs.cell_methods = 'time: sum (interval: 1 hour)'

    # Exit Definition Mode
    nc_file.sync()

    # Add Data Values
    var_time[:] = np.arange(len(t))
    var_time_bnds[:, 0] = time_bnds[:-1]
    var_time_bnds[:, 1] = time_bnds[1:]
    var_lat[:] = np.arange(A.grid.size[0]) * A.grid.dy + A.grid.y_range[0]
    var_lon[:] = np.arange(A.grid.size[1]) * A.grid.dx + A.grid.x_range[0]
    var_z[:] = c.metadata['depth_mean']
    var_z_bnds[:] = [0, c.metadata['depth_bottom']]
    var_u_avg[:] = u_avg
    var_v_avg[:] = v_avg
    var_u_var[:] = u_var
    var_v_var[:] = v_var
    var_u_min[:] = u_min
    var_v_min[:] = v_min
    var_u_max[:] = u_max
    var_v_max[:] = v_max
    var_n_obs[:] = n_obs

    # Close file
    nc_file.close()
