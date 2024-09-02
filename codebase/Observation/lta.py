"""

    LTA Long-term average velocity processing

	lta(c, logger) processes hourly total solutions to produce monthly
	and annual average velocity fields. In near real-time processing,
	there's a minimum month day defined before which no long-term average
	products will be made. Once the minimum month day is passed, monthly
	and annual average solutions are computed for the previous month
	and/or year.

	Reprocessing is indicated through the reprocess field in the
	configuration structure c.

	All logging is sent to the logger class.

    See also LTAMONTHLY, LTAANNUAL, PROCESSRTV, LOGGER


    HF-Radar Network
    Scripps Institution of Oceanography
    Coastal Observing Research and Development Center

"""
import datetime
import dateutil
# from dateutil import relativedelta
# from dateutil.relativedelta import relativedelta


def lta(c, logger):

	# Determine if we're reprocessing
	reprocessing = False
	if 'reprocess' in c:
		reprocessing = True

	# General tests
	timeNow = datetime.datetime.now()

	if reprocessing:
		# Define the start of the current month
		maxLtaDate = datetime.datetime(timeNow.year, timeNow.month, 1)
        
		# If we aren't past the min month day for monthly averages, shift date
		# back to the start of the previous month
		if not (timeNow.day >= c['lta']['monthly_min_month_day']):
			maxLtaDate -= relativedelta(months=1)

		# When RTV processing is enabled, determine if there are any averages
		# to (re)process based on rtvs that were reprocessed. Otherwise, use
		# the input time range for reprocessing.
		if 'RTV' in c['processes']['name']:
			newRtvTimes = c['reprocess']['tNewRtvFiles']
		else:
			newRtvTimes = c['reprocess']['times']

		# Determine if there are any averages to (re)process    
		if not any(newRtvTime < maxLtaDate for newRtvTime in newRtvTimes):
			logger.debug(f'No new RTVs processed prior to {maxLtaDate}, exiting')
			return

   elif not (timeNow.day >= c['lta']['monthly_min_month_day']):
		logger.debug(f'Below minimum month day ({c["lta"]["monthly_min_month_day"]}) for lta processing, exiting')
      return

   # Monthly Average Processing
	try:
		ltaMonthly(c, logger)
	except Exception as e:
		logger.error(f'Error processing {c["process"]["method"]} monthly average (lta): {str(e)}')

	# Annual Average Processing
	try:
		ltaAnnual(c, logger)
	except Exception as e:
		logger.error(f'Error processing {c["process"]["method"]} annual average (lta): {str(e)}')


