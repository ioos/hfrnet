# RTV Processing Toolbox
# Version 1.0.02 (R2019a) 25-Mar-2021
#
# Classes
#   FileLock           - FileLock  Exclusive file-based locking
#   Logger             - Logging class
#   State              - Create, Read, Update, and Delete program state
#
# Wrappers
#   processRtv         - Processes all RTV products
#   runRtv             - Batch wrapper for processRtv
#
# General functions
#   productVersion     - Returns the rtvproc product version
#   saveAscii          - Export velocity data to ASCII file
#   saveMat            - Save rtvproc data to MATLAB file
#
# Real-time vector (RTV) processing
#   rtv                - Process radials to totals
#   rtvComputeTotals   - Computes total solutions from radial velocities
#   rtvGetProcessTimes - Obtain RTV times to process
#   rtvGetSiteConfig   - Obtains time-dependent site configurations
#   rtvLoadRadials     - Loads radial data for RTV processing
#   rtvMergeData       - RTVMERGETOTALS Merges current data with previous run(s)
#   rtvReadRadialFile  - Read lluv radial file to structure
#   rtvSaveNetcdf      - Saves RTV data to a NetCDF file
#   uwlsTotal          - Computes a total velocity from radials using least-squares
#
# Sub-tidal current (STC) processing
#   findNewRtvs        - Obtain new RTVs
#   stc                - Sub-tidal current processing
#   stcCompute25hrAvg  - Compute 25-hour average velocity field
#   stcSaveNetcdf      - Saves STC data to a NetCDF file
#
# Long-term average (LTA) processing
#   lta                - Long-term average velocity processing
#   ltaAnnual          - Annual long-term averge velocity processing
#   ltaAnnualAvg       - Compute annual average velocity from monthly sums
#   ltaMonthly         - Monthly long-term average velocity processing
#   ltaMonthlyAvg      - Compute monthly average velocity from sums
#   ltaMonthlySum      - Compute monthly one-pass sums of hourly rtv velocities
#   ltaQCmask          - Apply quality control masks to long-term average products
#   ltaSaveNetcdf      - Saves LTA data to a NetCDF file

