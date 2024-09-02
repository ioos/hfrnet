"""

	RTV Process radials to totals

    tNewRtvFiles = rtv(c, logger) loads available radial data, computes
    total solutions, and saves results based on configuration parameters
    provided in c while logging to the logger object.

    Configuration parameters are defined in the dictionary c where the
    fields are required:
        process
        domain
        resolution
        landfile
        gridfile
        total
        getExternalProcessMetadata
        confdb

    The reprocess field is defined during reprocessing. The landmask and
    total grid are loaded into the land and grid fields, respectively.

    Processing iterates over each time step where the time-dependent site
    configurations are obtained for the domain and resolution, radial
    files are loaded, totals are computed and merged with any previous
    solutions, then finally saved to all configured formats which may
    include MAT, ASCII, and NetCDF files.

    State tracking is performed during near real-time processing only and
    is not used during reprocessing. The current and new state are
    obtained from rtvGetProcessTimes and the new state is written after
    all processing is completed.

    All logging is sent to the logger class.

    See also:
		LOGGER, RTVPROCCONF, RTVGETPROCESSTIMES, RTVGETSITECONFIG,
		RTVLOADRADIALS, RTVCOMPUTETOTALS, RTVMERGEDATA, SAVEMAT,
		SAVEASCII, RTVSAVENETCDF, STATE, CONFIGFUNCTION


   HF-Radar Network
   Scripps Institution of Oceanography
   Coastal Observing Research and Development Center

"""
import os
import logging
import datetime


def rtv( c, logger ):

	# Initialize return values
    tNewRtvFiles = []

    # Determine if we're reprocessing
    reprocessing = 'reprocess' in c

    # Define hours to process
	if reprocessing:
		processTimes = conf['reprocess']['times']
	else:
		processTimes = rtvGetProcessTimes(conf, logger)

	if len(processTimes):
		logger.info(f"Obtained {len(processTimes)} hour(s) to process between {min(processTimes)} and {max(processTimes)}")
	else:
		logger.info('No new radials found')
		return tNewRtvFiles

	# Load land mask and grid data
	# Land mask used on radials
	c['land'] = load(c['landfile'], c['domain'])
	c['land'] = c['land'][c['domain']]
	logger.debug(f"Loaded {c['domain']} land mask from {c['landfile']}")

   # Total grid
	gridvar = f"{c['domain']}{c['resolution']}"

   try:
		c['grid'] = load(c['gridfile'], gridvar)
		c['grid'] = c['grid'][gridvar]
	except Exception as e:
		errmsg = f"Error loading variable {gridvar} from {c['gridfile']}: {str(e)}"
		logger.error(errmsg)
		raise RuntimeError(f"rtvproc:rtvComputeTotals:variableLoadError: {errmsg}")

	logger.debug(f"Loaded {gridvar} from {c['gridfile']}")

   # Iterate over each hour
   idx = 0
   newFileMask = [False] * len(processTimes)
   for t in processTimes:
		ticValue = datetime.datetime.now()
		idx += 1

      if reprocessing:
			logger.info(f"Begin reprocessing rtv for {t}")
      else:
			logger.info(f"Begin processing rtv for {t}")

      # Iteration specific config
      ci = c.copy()
      ci = ci['total'].getFilenames(ci, t)  # generate rtv file names

      # Get time-dependent site configurations
      ci = rtvGetSiteConfig(ci, logger, t)

		if 'site' not in ci:
			logger.alert('No sites configured for RTV processing at this time')
			continue #..goto next iteration

		logger.info(f"Obtained configurations for {len(ci['site'])} sites")

		if len(ci['site']) < ci['rtv']['min_rad_sites']:
			logger.warning(f"The number of sites configured ({len(ci['site'])}) is less than the minimum number of sites required to produce a solution ({ci['rtv']['min_rad_sites']})")
			continue #..goto next iteration

		# If reprocessing, remove any existing total files
		if reprocessing:
			rtvRmTotalFiles(ci, logger)

		# Load radial data
		ci, r = rtvLoadRadials(ci, logger, t)

		if not r:
			logger.info('No radial data obtained')
			continue #..goto next iteration

		nSites = len(r)

		if nSites < 2:
			logger.info('Only obtained data from one site')
			continue #..goto next iteration

		logger.info(f"Obtained radial data from {nSites} sites")

		# Compute totals
		U = rtvComputeTotals(ci, logger, r)

		if not U:
			logger.info('No total solutions returned')
			continue #..goto next iteration

		# Add history and merge with previous solutions
		r, U = rtvMergeData(ci, logger, r, U)

		# Save data
		# Get process (i.e. rtv & method) specific metadata
		ci = ci.getExternalProcessMetadata(ci)

		# Save MAT file
		success, message = saveMat(ci, t, U, r)

		if not success:
			errmsg = f"Error saving rtvs to mat-file; {message}"
			logger.error(errmsg)
			raise RuntimeError(f"rtvproc:rtv: {errmsg}")

		logger.info('Saved rtv solutions to mat-file')

		# Save ASCII file
		if 'ascii' in ci['process']['saveas'].lower():
			if any(u['hdop'] <= ci['rtv']['uwls_max_hdop_ascii'] for u in U):
				success, message = saveAscii(ci, U)
				if not success:
					errmsg = f"Error saving rtvs to ascii file; {message}"
					logger.error(errmsg)
					raise RuntimeError(f"rtvproc:rtv: {errmsg}")

				logger.info('Saved rtv solutions to ascii file')
			else:
				logger.info('No total solutions below ascii hdop threshold')

		# Save NetCDF
		if 'netcdf' in ci['process']['saveas'].lower():
			if any(u['hdop'] <= ci['rtv']['uwls_max_hdop_nc'] for u in U):
				success, message = rtvSaveNetcdf(ci, t, U, r)
				if not success:
					 errmsg = f"Error saving rtvs to netcdf file; {message}"
					 logger.error(errmsg)
					 raise RuntimeError(f"rtvproc:rtv: {errmsg}")

				logger.info('Saved rtv solutions to netcdf file')
			else:
				logger.info('No total solutions below netcdf hdop threshold')

		# Record processed timestamp
		newFileMask[idx - 1] = True

		# Log elapsed time
		elapsedTime = datetime.datetime.now() - ticValue
		logger.info(f"Iteration elapsed time {elapsedTime}")

	# Populate return value
	tNewRtvFiles = [processTimes[i] for i in range(len(processTimes)) if newFileMask[i]]

	# Update state
	if not reprocessing:
		state = State(c['domain'], c['resolution'], 'rtv', c['confdb'])
		state.get()
		state.time = c['rtv']['new_state']
		state.write()
		logger.debug(f"Updated rtv state to {state.time}")
		state.delete()
		del state

	return tNewRtvFiles

#. . . .. . . . . .. . . . . .. . . . . .. . . . . .. . . . . .. . . . . .. . . . . .. . . . . .. . 

def rtvRmTotalFiles(c, logger):
	"""
	RTVRMTOTALFILES Removes any existing total files
	"""

	filefields = ["mpathfile", "asciipathfile", "ncpathfile"]

	for filefield in filefields:
		pathfile = c['total'][filefield]

		if os.path.exists(pathfile):
			try:
				os.remove(pathfile)
				logger.debug(f"Deleted {pathfile}")
			except Exception as e:
				errmsg = f"Error removing {pathfile}: {str(e)}"
				logger.error(errmsg)
				raise RuntimeError(f"rtvproc:rtv:rtvRmTotalFiles:deleteError: {errmsg}")

#.end
