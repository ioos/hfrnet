"""
  
  This class handles radial files.

  Changes
    2018-09-04 - Initial version
    2018-09-10 - Added functions and variables to input data into the database 
    2018-12-06 - PatternType check for lowercase values
    2018-12-07 - ellip_flatten - remove characters that aren't numbers or a period
    2018-12-17 - Round modification time to 5 decimals. Updated getRadialMetaSQLInsert to use getModificationTime
    2019-01-11 - Added try/except in __getTableData() when making our datetime.  Some files RDL_i_BML_BML1_2016_10_20_0900.hfrss10lluv have weird values
    2019-01-11 - Bug: getPatternType() changed lower to lower()
    2019-01-25 - Bug: getStationNetworkID(): Added n.net in WHERE clause
    2019-02-11 - Bug: GetStationNetworkID(): Added quotes around string where clauses
    2019-03-05 - Added db.commit after each executeQuery in insertIntoDB. Call closeDBConnection at the end. 
    2019-06-11 - Bug: filenameRegEx(): Network name from {2,6} to {2,25}
    2019-07-24 - Bug: Added tzinfo into datetime functions 
    2019-09-25 - Added option to connect with ssl for data database
    2020-01-07 - Added try/except for isValidLatLon.  In case we aren't able to convert to float.
    2020-10-08 - Added validCTFdata
    2020-10-23 - Add try/except in insertIntoDB and return false if exception
    2021-01-04 - Changed isCodarFile to look for CODAR
    2021-08-27 - Added validResolution
    2021-11-25 - Bug: Call self.validResolution() and not self.validResolution from validFile. 
               - Added in getTableData(), check to make sure 'inf' isn't in the data
    2022-01-24 - Bug: checkValue, checkFloatValue, checkIntValue, getRadialMeta.  Assign 'DEFAULT' for 'inf' or 'nan'
    2022-10-28 - Bug: checkFloatValue, checkIntValue.  Added try statements in case the value isn't a valid float or int
    2023-02-18 - Bug: checkIntValue.   int(float()).  String float will give an error if just int()


"""
from lib.cordc_lib import grep, retrieveBetweenTwoPatterns, is_number
import re
import os
import logging
import subprocess
from datetime import datetime
from datetime import timezone
import configparser
import pymysql
import sys
import traceback


class RadialFile:
 
  hardwareDiagnosticsSQLColumns = {"TMP":"receiver_chassis_tmp",
                                   "MTMP":"awg_tmp",
                                   "XTRP":"transmit_trip",
                                   "RUNT":"awg_run_time",
                                   "SP24":"receiver_supply_p24vdc",
                                   "SP05":"receiver_supply_p5vdc",
                                   "SN05":"receiver_supply_n5vdc",
                                   "SP12":"receiver_supply_p12vdc",
                                   "XPHT":"xmit_chassis_tmp",
                                   "XAHT":"xmit_amp_tmp",
                                   "XAFW":"xmit_fwd_pwr",
                                   "XARW":"xmit_ref_pwr",
                                   "XP28":"xmit_supply_p28vdc",
                                   "XP05":"xmit_supply_p5vdc",
                                   "GRMD":"gps_receive_mode",
                                   "GDMD":"gps_discipline_mode",
                                   "PLLL":"npll_unlock",
                                   "HTMP":"receiver_hires_tmp",
                                   "HUMI":"receiver_humidity",
                                   "RBIA":"vdc_draw",
                                   "CRUN":"cpu_runtime"}
  radialDiagnosticsSQLColumns = {"AMP1":"loop1_amp_calc",
                                 "AMP2":"loop2_amp_calc",
                                 "PH13":"loop1_phase_calc",
                                 "PH23":"loop2_phase_calc",
                                 "CPH1":"loop1_phase_corr",
                                 "CPH2":"loop2_phase_corr",
                                 "SNF1":"loop1_css_noisefloor",
                                 "SNF2":"loop2_css_noisefloor",
                                 "SNF3":"mono_css_noisefloor",
                                 "SSN1":"loop1_css_snr",
                                 "SSN2":"loop2_css_snr",
                                 "SSN3":"mono_css_snr",
                                 "DGRC":"diag_range_cell",
                                 "DOPV":"valid_doppler_cells",
                                 "DDAP":"dual_angle_pcnt",
                                 "RADV":"rad_vect_count",
                                 "RAPR":"avg_rads_per_range",
                                 "RARC":"nrange_proc",
                                 "RADR":"rad_range",
                                 "RMCV":"max_rad_spd",
                                 "RACV":"avg_rad_spd",
                                 "RABA":"avg_rad_bearing",
                                 "RTYP":"rad_type",
                                 "STYP":"spectra_type"}
  radialMetaSQLColumns = { "TransmitCenterFreqMHz":"cfreq",
                           "RangeResolutionKMeters":"range_res",
                           "TableRows":"nrads",
                           "DopplerResolutionHzPerBin":"dres",
                           "Manufacturer":"manufacturer",
                           "TransmitSweepRateHz":"xmit_sweep_rate",
                           "TransmitBandwidthKHz":"xmit_bandwidth",
                           "CurrentVelocityLimit":"max_curr_lim",
                           "RadialMinimumMergePoints":"min_rad_vect_pts",
                           "BraggSmoothingPoints":"bragg_smooth_pts",
                           "RadialBraggPeakDropOff":"rad_bragg_peak_dropoff",
                           "BraggHasSecondOrder":"second_order_bragg",
                           "RadialBraggPeakNull":"rad_bragg_peak_null",
                           "RadialBraggNoiseThreshold":"rad_bragg_noise_thr",
                           "CTF":"ctf_ver",
                           "SpectraRangeCells":"spec_range_cells",
                           "SpectraDopplerCells":"spec_doppler_cells",
                           "FirstOrderCalc":"first_order_calc",
                           "MergedCount":"nmerge_rads",
                           "RangeStart":"range_bin_start",
                           "RangeEnd":"range_bin_end"}
  old_radialMetaSQLColumns = { #"format": "",
                           "lat" : "Origin",
                           "lon" : "Origin",
                           "cfreq" : "TransmitCenterFreqMHz",
                           "range_res" : "RangeResolutionKMeters",
                           "ref_bearing" : "ReferenceBearing",
                           "nrads" : "TableRows",
                           "dres" : "DopplerResolutionHzPerBin",
                           "manufacturer" : "Manufacturer",
                           "xmit_sweep_rate" : "TransmitSweepRateHz",
                           "xmit_bandwidth" : "TransmitBandwidthKHz",
                           "max_curr_lim" : "CurrentVelocityLimit",
                           "min_rad_vect_pts" : "RadialMinimumMergePoints",
                           "loop1_amp_corr" : "PatternAmplitudeCorrections",
                           "loop2_amp_corr" : "PatternAmplitudeCorrections",
                           "loop1_phase_corr" : "PatternPhaseCorrections",
                           "loop2_phase_corr" : "PatternPhaseCorrections",
                           "bragg_smooth_pts" : "BraggSmoothingPoints",
                           "rad_bragg_peak_dropoff" : "RadialBraggPeakDropOff",
                           "second_order_bragg" : "BraggHasSecondOrder",
                           "rad_bragg_peak_null" : "RadialBraggPeakNull",
                           "rad_bragg_noise_thr" : "RadialBraggNoiseThreshold",
                           "music_param_01" : "RadialMusicParameters",
                           "music_param_02" : "RadialMusicParameters",
                           "music_param_03" : "RadialMusicParameters",
                           "ellip" : "GreatCircle",
                           #"earth_radius" : "",
                           "ellip_flatten" : "GreatCircle",
                           "ctf_ver" : "CTF",
                           "lluvspec_ver" : "LLUVSpec",
                           "geod_ver" : "GeodVersion",
                           "patt_date" : "PatternDate",
                           "patt_res" : "PatternResolution",
                           "patt_smooth" : "PatternSmoothing",
                           "spec_range_cells" : "SpectraRangeCells",
                           "spec_doppler_cells" : "SpectraDopplerCells",
                           #"curr_ver" : "",
                           #"codartools_ver" : "",
                           "first_order_calc" : "FirstOrderCalc",
                           "lluv_tblsubtype" : "TableType",
                           #"proc_by" : "",
                           "merge_method" : "MergeMethod",
                           "patt_method" : "PatternMethod",
                           #"dir" : "",
                           #"dfile" : "",
                           #"mtime" : "",
                           #"sampling_period_hrs" : "",
                           "nmerge_rads" : "MergedCount",
                           "range_bin_start" : "RangeStart",
                           "range_bin_end" : "RangeEnd",
                           "loop1_amp_calc" : "PatternAmplitudeCalculations",
                           "loop2_amp_calc" : "PatternAmplitudeCalculations",
                           "loop1_phase_calc" : "PatternPhaseCalculations",
                           "loop2_phase_calc" : "PatternPhaseCalculations"}
  processingToolData = { "RadialMerger":"rad_merger_ver",
                         "SpectraToRadial":"spec2rad_ver",
                         "RadialSlider":"rad_slider_ver",
                         "RadialArchiver":"rad_archiver_ver",
                         "codar_rb2lluv.pl":"codartools_ver", # not sure if this is correct
                         "Currents":"curr_ver",
                         "ProcessedTimeStamp":"proc_time"}
 
  def __init__(self,filename):
    """
    The constructor for the RadialFile class.
    
    @params:
      filename (str) - The path and filename of the radial file.
    """
    self.filename = filename
    self.isCodar = self.isCodarFile()
    self.modificationTime = self.getModificationTime()
    self.config = configparser.ConfigParser()

  def getModificationTime(self):
    """
    Returns the modification time of the radial file
    
    Returns:
      epoch timestamp
    """
    return round(os.path.getmtime(self.filename),5)
  # End getModificationTime  
 
  def getPatternType(self):
    """
    Returns the patern type m/i
    @return str i/m
    """
    pattern = "^\s*%PatternType:"
    result = grep(pattern,self.filename)

    # Some Wera (SC) have no pattern type, return i
    if not result: return "i"

    pattern = re.compile("^\s*%PatternType:\s+([A-Za-z]{3,})")
    match = pattern.search(result)
    if match.group(1).lower() == "measured":
      return "m"
    else:
      return "i"
  # End getPatternType
  
  def isCodarFile(self):
    """
    Checks to see if the radial files is from codar
    
    Returns:
      True if codar, False if not
    """
    #pattern = "%Manufacturer:.*(W|L)ERA";
    #result = grep( pattern, self.filename )
    #if not result:
    #  return True
    #return False

    pattern = "%Manufacturer:.*CODAR";
    result = grep( pattern, self.filename )
    if result:
      return True
    return False
  
  def validCTFdata(self):
    """
    Checks to see if the file starts with CTF
    
    Returns:
      True/False
    """
    pattern = "%CTF"
    result = grep( pattern, self.filename )
    if not result:
      logging.error("CTF not found")
      return False
    return True

  def validSiteMetadata(self):
    """
    Checks to see if the site metadata is in the file.
    
    Returns:
      True/False
    """
    pattern = "^\s*%Site:\s+\w{3,4}"
    result = grep( pattern, self.filename )
    if not result:
      logging.error("Site metadata not found")
      return False
    return True

  def validTimeStampMetadata(self):
    """
    Checks if the TimeStamp metadata is valid.
    
    Returns: True/False
    """
    pattern = "^\s*%TimeStamp:\s+[0-9]{4}\s+[0-9]{1,2}\s+[0-9]{1,2}\s+[0-9]{1,2}\s+[0-9]{1,2}\s+[0-9]{1,2}" 
    result = grep( pattern, self.filename )
    if not result:
      logging.error("TimeStamp metadata not found or invalid")
      return False
    return True

  def validTimeZoneMetadata(self):
    """
    Checks if the TimeZone metadata is valid.
    
    Returns: True/False
    """
    pattern = "^\s*%TimeZone:\s+(\")?(GMT|UTC)(\")?"
    result = grep( pattern, self.filename )
    if not result:
      logging.error("TimeZone metadata not found or invalid")
      return False
    return True

  def validPatternTypeMetadata(self):
    """
    Checks if the PatternType metadata is valid.
    
    Returns: True/False
    """
    pattern = "^\s*%PatternType:\s+[A-Za-z]{3,}"
    result = grep( pattern, self.filename )
    if not result:
      logging.error("PatternType metadata not found or invalid")
      return False
    return True

  def validLatLon(self):
    """
    Checks if the Lat/Lon metadata is valid.
    
    Returns: True/False
    """
    # %Origin:  32.5359167 -117.1222667
    pattern = "^\s*%Origin:"
    result = grep( pattern, self.filename )
    key,lat,lon = result.split() 
    try:
      if float(lat) < -90 or float(lat) > 90 or float(lon) < -180 or float(lon) > 180:
        logging.error("Invalid lat,lon: %s,%s",lat,lon)
        return False
    except ValueError:
      logging.error("Invalid lat,lon: %s,%s",lat,lon)
      return False
    return True

  def validResolution(self):
    """
    Checks if the RangeResolution metadata is valid

    Returns: True/False
    """
    pattern = "^\s*%RangeResolution.+[0-9]"
    result = grep( pattern, self.filename )
    if not result:
      logging.error("Resolution metadata not found or invalid")
      return False
    return True

  def validLLUV_RDLTable(self):
    """
    Checks if the LLUV RDL table type is valid.
    
    Returns: True/False
    """
    pattern = "^\s*%TableType:\s+LLUV\s+RDL"
    result = grep( pattern, self.filename )
    if not result:
      logging.error("Table type LLUV RDL not defined")
      return False

    pattern = "^\s*[^%]"
    result = grep( pattern, self.filename )
    if not result:
      logging.error("No radial data found")
      return False

    result = retrieveBetweenTwoPatterns("%TableType","%TableEnd", self.filename)
    if not result:
      logging.error("Radial tables not found")
      return False
    pattern = re.compile("%TableColumns:\s+([0-9]+)")
    match = pattern.search(result)
    if not match:
      logging.error("TableColumns not found")
      return False
    columns = match.group(1)

    pattern = re.compile("%TableColumnTypes:.+\n")
    match = pattern.search(result)
    if not match:
      logging.error("TableColumnTypes not found")
      return False
    columnTypes = len(match.group(0).split())
    if str(columnTypes - 1) != str(columns):
      logging.error("Number of columns does not match TableColumns")
      return False
 
  
    return True

  def validFile(self):
    """
    Checks if the radial file is valid. Performs all of the valid* functions.
    
    Returns: True/False
    """
    if not self.validCTFdata(): return False
    if not self.validSiteMetadata(): return False
    if not self.validTimeStampMetadata(): return False
    if not self.validTimeZoneMetadata(): return False
    if not self.validLatLon(): return False
    if not self.validLLUV_RDLTable(): return False
    if not self.validResolution(): return False

    if self.isCodar:
      if not self.validPatternTypeMetadata(): return False

    return True

  def __getHeaders(self,line):
    """ 
    Return the headers for a particular section as an array with the header name being the value 
    and the key being the index 
  
    @param string $line Line containing the header
  
    @return array Returns the header name as the value and the key being the index
    """
    line_split = line.split(":")
    return line_split[1].strip().split(" ")
  # End  __getHEaders

  def __getTableData(self,start,end,starttime=None, endtime=None):
    """
    Get the data for a specific table type
  
    @param string $start The Start of the table e.g. '%TableType: rads rad1' 
    @param string $end The end of the table e.g. '%TableEnd: 2'
    @param int $starttime optional Epoch start time 
    @param int $endtime optional Epoch end time
  
    @return array Associative array with keys being the column type (TIME,AMP1...) and values being the data
    """
    data = []
    alldata = []
    headerfound = False;

    # Use sed to extract the data and put into variable $lines
    sed = ["sed", "-e", "/"+start+"/,/"+end+"/!d", self.filename]

    try:
      completed = subprocess.check_output(sed,stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as exc:
      logging.error("sed failed: %s", exc.output.decode('ascii'))
    else:
      # 'ignore' is there because in some files (SIO) the column units  have weird characters that
      # won't decode correct and it gives an error
      lines = completed.decode('ascii','ignore').split('\n')
      if len(lines) == 0: return None 
      for line in lines:
        # Header
        p = re.compile('%TableColumnTypes')
        if p.match( line ):
          headers = self.__getHeaders(line)
          headerfound = True
        if headerfound == False: continue
        # Data
        line = line.strip("%")
        line = line.strip()
        if len(headers) == len( line.split(None) ) :
          # if line contains inf or nan, insert 'DEFAULT' use default values for those
          if "inf" in line:
            line = line.replace('inf','DEFAULT')
            logging.warning("invalid entry, %s",line)
          if "nan" in line:
            line = line.replace('nan','DEFAULT')
            logging.warning("invalid entry, %s",line)

          data = line.split( None );
          # Skip anything that isn't our data
          if not is_number(data[0]): continue
          data = dict(zip(headers,data))

          # Get the date only for radial diagnostics and hardware diag.  lluv data doesn't have dates
          if "THRS" in data:

            # Make sure the dates and times are correct
            # RDL_i_BML_BML1_2016_10_20_0900.hfrss10lluv has some weird values
            try:
              date = datetime(int(data["TYRS"]),int(data["TMON"]),int(data["TDAY"]),int(data["THRS"]),int(data["TMIN"]),int(data["TSEC"]),tzinfo=timezone.utc).timestamp()
            except:
              logging.error("__getTableData() datetime(){}".format(line))
              continue

            if starttime != None :
              if date < starttime: continue
            if endtime != None :
              if date > endtime: continue
          alldata.append(data)
      return alldata
  # End __getTableData

  def getRadialDiagnostics(self):
    """
    Gets the data from the 'rads rad' table.  
  
    @return array Associative array with keys being the column type (TIME, AMP1...) and values being the data 
    """ 
    return self.__getTableData("%TableType: rads rad","%TableEnd")
  # End getRadialDiagnostics

  def getHardwareDiagnostics(self):
    """
    Gets the data from the 'rcvr rcv' table.  
   
    @return array Associative array with keys being the column type (TIME, AMP1...) and values being the data 
    """ 
    data=self.__getTableData("%TableType: rcvr rcv","%TableEnd")
    return data
  # End  getHardwareDiagnostics

  def getLLUVData(self):
    """
    Gets the data from the 'LLUV RDL' table.  
  
    @return array Associative array with keys being the column type (TIME, AMP1...) and values being the data 
    """
    return self.__getTableData("%TableType: LLUV RDL","%TableEnd:")
  # End  getLLUVData

  def getDiskUsage(self):
    """
    Gets the data containing disk usage
  
    @return array Associative array with keys being the column type and values being data
    """  
    datas = [] 
    data = {}
    result = grep( "DISK", self.filename )
    if not result:
      return data
    for line in result.split('\n'):
      df = line.split()
      if len(df) == 7 :
        data = {}
        data["filesystem"] = df[1]
        data["1M-blocks"] = df[2]
        data["used"] = df[3]
        data["available"] = df[4]
        data["use_percent"] = df[5].replace("%","")
        data["mounted_on"] = df[6]
        datas.append(data)
    return datas
  # End  getDiskUsage

  def getProcessInfo(self,sql=True):
    """
    Gets the data containing text with 'Process', generally the end of the file.  

    @param boolean - True will return the data using the sql column name as the key.  Default true
    @return array Associative array with keys being the column type (TIME, AMP1...) and values being the data 
    """
    data = {}

    result = grep("Process",self.filename )
    if not result:
      return data

    for line in result.strip().split('\n'): 
      if "ProcessedTimeStamp" in line:
        arr = line.split()
        # If the seconds/minutes equals 60, then change it to 59
        if int(arr[5]) == 60: arr[5] = 59
        if int(arr[6]) == 60: arr[6] = 59
        try:
          data[ "ProcessedTimeStamp" ] = datetime(int(arr[1]),int(arr[2]),int(arr[3]),int(arr[4]),int(arr[5]),int(arr[6]),tzinfo=timezone.utc ).timestamp()
        except:
          logging.error("getProcessInfo(): There was an error processing the timestamp: {}.  Skipping line".format(line)) 
          continue
      else :
        arr = line.split()
        data[ arr[1].replace('"','') ] = arr[2]
    
    if sql==False: return data

    return self.convertMetaToSQL(data, self.processingToolData)

  # End  getProcessInfo

  def getRadialMeta(self,sql=True):
    """
    Gets the meta data   
    @param boolean - True will return the data using the sql column name as the key.  Default true
    @return array - Associative array with keys being the column type (TIME, AMP1...) and values being the data 
    """
    data = {} 
    start = "%CTF"
    end = "%TableRows"

    sed = ["sed", "-e", "/"+start+"/,/"+end+"/!d", self.filename]
    try:
      completed = subprocess.check_output(sed,stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as exc:
      logging.error("sed failed: %s", exc.output.decode('ascii'))
      return None

    lines = completed.decode('ascii','ignore').strip().split('\n')
    if len(lines) == 1: return None
  
    for line in lines:
      line = line.strip("%")
      line = line.strip("%")
      line = line.split(":",1 )
      data[ line[0] ] = line[1].strip()

    if sql == False: return data

    dataSQL = {}
    for key, value in data.items():
      if "nan" in value:
        logging.warning("invalid entry %s for %s",value,key)
        continue
      arr = value.split()

      if key=="RangeResolutionMeters":
        dataSQL["range_res"] = '%.4f'%(float(arr[0]) /1000)
      elif key=="LLUVSpec":
        dataSQL["lluvspec_ver"] = arr[0]
      elif key== "Origin":
        dataSQL["lat"] = '%.6f'%(float(arr[0]))
        dataSQL["lon"] = '%.6f'%(float(arr[1]))
      elif key== "GreatCircle":
        dataSQL["ellip"] = arr[0].strip('"')
        # Remove characters that aren't numbers or a period
        # Mainly for WHOI:LPWR - have a single quote at the end
        non_decimal = re.compile(r'[^\d.]+')
        dataSQL["ellip_flatten"] = arr[2]
        dataSQL["ellip_flatten"] = non_decimal.sub("",arr[2])
      elif key== "GeodVersion":
        pattern = re.compile('(\".+\")\s+(\d+\.\d+)\s+')
        arr = pattern.findall(value) 
        dataSQL["geod_ver"] = arr[0][0].strip('"')+" "+arr[0][1]
          
      elif key== "ReferenceBearing":
        dataSQL["ref_bearing"] = '%.4f'%(float(arr[0]))
      elif key== "PatternDate":
        dataSQL["patt_date"] = datetime(int(arr[0]),int(arr[1]),int(arr[2]),int(arr[3]),int(arr[4]),int(arr[5]),tzinfo=timezone.utc).timestamp()
      elif key== "PatternResolution":
        dataSQL["patt_res"] = '%.2f'%(float(arr[0]))
      elif key== "PatternSmoothing":
        dataSQL["patt_smooth"] = '%.2f'%(float(arr[0]))
      elif key== "PatternAmplitudeCorrections":
        dataSQL["loop1_amp_corr"] = '%.2f'%(float(arr[0]))
        dataSQL["loop2_amp_corr"] = '%.2f'%(float(arr[1]))
      elif key== "PatternPhaseCorrections":
        dataSQL["loop1_phase_corr"] = '%.2f'%(float(arr[0]))
        dataSQL["loop2_phase_corr"] = '%.2f'%(float(arr[1]))
      elif key== "PatternAmplitudeCalculations":
        dataSQL["loop1_amp_calc"] = '%.2f'%(float(arr[0]))
        dataSQL["loop2_amp_calc"] = '%.2f'%(float(arr[1]))
          
      elif key== "PatternPhaseCorrections":
        dataSQL["loop1_phase_corr"] = '%.2f'%(float(arr[0]))
        dataSQL["loop2_phase_corr"] = '%.2f'%(float(arr[1]))
          
      elif key== "PatternAmplitudeCalculations":
        dataSQL["loop1_amp_calc"] = '%.2f'%(float(arr[0]))
        dataSQL["loop2_amp_calc"] = '%.2f'%(float(arr[1]))
          
      elif key== "PatternPhaseCalculations":
        dataSQL["loop1_phase_calc"] = '%.2f'%(float(arr[0]))
        dataSQL["loop2_phase_calc"] = '%.2f'%(float(arr[1]))
          
      elif key== "RadialMusicParameters":
        dataSQL["music_param_01"] = '%.2f'%(float(arr[0]))
        dataSQL["music_param_02"] = '%.2f'%(float(arr[1]))
        dataSQL["music_param_03"] = '%.2f'%(float(arr[2]))
          
      elif key== "MergeMethod":
        dataSQL["merge_method"] = arr[0]
          
      elif key== "TableType":
        dataSQL["lluv_tblsubtype"] = arr[1]
          
      elif key== "TimeStamp":
        dataSQL["time"] = datetime(int(arr[0]),int(arr[1]),int(arr[2]),int(arr[3]),int(arr[4]),int(arr[5]),tzinfo=timezone.utc).timestamp() 
        dataSQL["endtime"] = datetime(int(arr[0]),int(arr[1]),int(arr[2]),int(arr[3]),int(arr[4]),int(arr[5]),tzinfo=timezone.utc).timestamp() 
          
      elif key== "TimeCoverage":
        dataSQL["sampling_period_hrs"] = '%.4f'%(float(arr[0])/60)
          
      elif key== "PatternMethod":
        dataSQL["patt_method"] = arr[0]
          
      else:
        if key in self.radialMetaSQLColumns:
          dataSQL[self.radialMetaSQLColumns[key]] = value
        else:  
          dataSQL[key] = value
    # end for key, value in data
    return dataSQL;
  # End function getRadialMeta

  def getRadialFileMeta(self):
    """
    Combines the data from radial meta and process info
  
    @return array Associative array with keys being the column type (TIME, AMP1...) and values being the data 
    """
    z = self.getRadialMeta().copy()
    z.update(self.getProcessInfo())
    return z
  # End function getRadialFileMeta

  def convertMetaToSQL(self,data,sqlColumns):
    """
    Converts variables from the lluv files to their respective sql variable name
  
    @param array string $data array containing the lluv variables
    @param array string $sqlColumns Array containing the mapped sql columns
    @return array Associative array with keys being the db column type (TIME, AMP1...) and values being the data 
    """
    data2 = {}
    if data == None: return data2 
    for key, value in data.items():
      if key in sqlColumns:
        data2[ sqlColumns[key] ] = data[key]
      else:
        logging.debug(key+" not found in convertMetaToSQL()")
        data2[key] = data[key]
    return data2
  # End convertMetaToSQL

  def __getNetworkName(self):
    """
    Get the short network name from the filename
    @return str network
    """
    net = self.__filenameRegEx(1)
    return net
  # End __getNetwork

  def __getStationName(self):
    """
    Get the short station name from the filename
    RDL_m_SIO_SDBP_2018_06_04_2100.hfrss10lluv
    RDL_UH_KAK_2018_06_05_0700.hfrweralluv1.0
    RDL_USF_VEN_2018_06_05_1700.hfrweralluv1.0

    @return str station
    """
    sta = self.__filenameRegEx(2)
    return sta
  # End __getStationName

  def __getYearMonth(self):
    """
    Get the year and month from the filename
    @return str <year>-<month> (2018-08)
    """
    year = self.__filenameRegEx(3)
    month = self.__filenameRegEx(4)
    return "{}-{}".format(year,month)
  # end __getYearMonth

  def __getFileDateTime(self):
    """
    Get the date/time from the filename
    @return epoch timestamp
    """
    year = self.__filenameRegEx(3)
    month = self.__filenameRegEx(4)
    day = self.__filenameRegEx(5)
    time = re.findall('..',self.__filenameRegEx(6))
    return datetime(int(year),int(month),int(day),int(time[0]),int(time[1]),0,tzinfo=timezone.utc).timestamp()
  # end __getFileDate
   
  def getFileDateTime(self):
    """
    Get the date/time from the filename
    @return epoch timestamp
    """
    return self.__getFileDateTime()
  # end __getFileDateTime
 
  def __filenameRegEx(self,groupid):
    """ 
    Return specific parts of the filename
    
    @param int group number from regex to return
    @return str
    """
    pattern = re.compile("RDL.+?([a-zA-Z0-9]{2,25})_([a-zA-Z0-9]{3,6})_(\d{4})_(\d{2})_(\d{2})_(\d{4}).(.*)")
    match = pattern.search(self.filename)
    if not match:
      logging.error("Unable to find a match in {} ".format(self.filename))
      return None
    return match.group(groupid)
  # end  __filenameRegEx

  def __checkStationNetworkID(self):
    """
    Checks to see if site_id and network_id variables are set.  If not, set it
    """
    
    try:
      self.__site_id
    except AttributeError:
      # Get site_id and network_id
      site_networkID = self.getStationNetworkID()
      self.__site_id = site_networkID["site_id"]
      self.__network_id = site_networkID["network_id"]
  # end def __checkStationNetworkID
    
  def getHardwareDiagnosticsSQLInsert(self):
    """ 
    Returns the sql used to insert hardware diagnostics data into the database

    @return str insert SQL
    """
    my_lists = []
    datas = self.getHardwareDiagnostics()
    if not datas: return datas 
    self.__checkStationNetworkID()

    for data in datas:
      mydate = datetime(int(data["TYRS"]),int(data["TMON"]),int(data["TDAY"]),int(data["THRS"]),int(data["TMIN"]),int(data["TSEC"]),tzinfo=timezone.utc).timestamp() 
      #my_list = []
      my_lists.append("({},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{})".format( self.__site_id,self.__network_id,mydate,self.__checkIntValue("RTMP",data),self.__checkIntValue("MTMP",data),self.__checkValue("XTRP",data),self.__checkIntValue("RUNT",data),self.__checkFloatValue("SP24",data),self.__checkFloatValue("SP05",data),self.__checkFloatValue("SN05",data),self.__checkFloatValue("SP12",data),self.__checkIntValue("XPHT",data),self.__checkIntValue("XAHT",data),self.__checkIntValue("XAFW",data),self.__checkIntValue("XARW",data),self.__checkFloatValue("XP28",data),self.__checkFloatValue("XP05",data),self.__checkIntValue("GRMD",data),self.__checkIntValue("GDMD",data),self.__checkIntValue("PLLL",data),self.__checkFloatValue("HTMP",data),self.__checkIntValue("HUMI",data),self.__checkFloatValue("RBIA",data),self.__checkFloatValue("CRUN",data)))

      #my_list.extend( [self.__site_id,self.__network_id,mydate,self.__checkIntValue("RTMP",data),self.__checkIntValue("MTMP",data),self.__checkValue("XTRP",data),self.__checkIntValue("RUNT",data),self.__checkFloatValue("SP24",data),self.__checkFloatValue("SP05",data),self.__checkFloatValue("SN05",data),self.__checkFloatValue("SP12",data),self.__checkIntValue("XPHT",data),self.__checkIntValue("XAHT",data),self.__checkIntValue("XAFW",data),self.__checkIntValue("XARW",data),self.__checkFloatValue("XP28",data),self.__checkFloatValue("XP05",data),self.__checkIntValue("GRMD",data),self.__checkIntValue("GDMD",data),self.__checkIntValue("PLLL",data),self.__checkFloatValue("HTMP",data),self.__checkIntValue("HUMI",data),self.__checkFloatValue("RBIA",data),self.__checkFloatValue("CRUN",data)])
      #my_lists.append(my_list)

    return my_lists
  # end  __getHardwareDiagnosticsSQLInsert

  def getRadialDiagnosticsSQLInsert(self):
    """ 
    Returns the sql used to insert Radial diagnostics data into the database

    @return str insert SQL
    """
    my_lists = []
    datas = self.getRadialDiagnostics()
    if not datas: return datas

    # Get pattern type
    patterntype = self.getPatternType()

    self.__checkStationNetworkID()

    for data in datas:
      mydate = datetime(int(data["TYRS"]),int(data["TMON"]),int(data["TDAY"]),int(data["THRS"]),int(data["TMIN"]),int(data["TSEC"]),tzinfo=timezone.utc).timestamp() 
      #my_list = []
      #my_list.extend([self.__site_id,self.__network_id,mydate,patterntype,float(data["AMP1"]),float(data["AMP2"]),float(data["PH13"]),float(data["PH23"]),float(data["CPH1"]),float(data["CPH2"]),float(data["SNF1"]),float(data["SNF2"]),float(data["SNF3"]),float(data["SSN1"]),float(data["SSN2"]),float(data["SSN3"]),int(data["DGRC"]),int(data["DOPV"]),int(data["DDAP"]),int(data["RADV"]),int(data["RAPR"]),int(data["RARC"]),float(data["RADR"]),float(data["RMCV"]),float(data["RACV"]),float(data["RABA"]),int(data["RTYP"]),int(data["STYP"])])
      my_lists.append("({},{},{},'{}',{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{})".format( self.__site_id,self.__network_id,mydate,patterntype,self.__checkFloatValue("AMP1",data,4),self.__checkFloatValue("AMP2",data,4),self.__checkFloatValue("PH13",data,4),self.__checkFloatValue("PH23",data,4),self.__checkFloatValue("CPH1",data,4),self.__checkFloatValue("CPH2",data,4),self.__checkFloatValue("SNF1",data,4),self.__checkFloatValue("SNF2",data,4),self.__checkFloatValue("SNF3",data,4),self.__checkFloatValue("SSN1",data),self.__checkFloatValue("SSN2",data),self.__checkFloatValue("SSN3",data),self.__checkIntValue("DGRC",data),self.__checkIntValue("DOPV",data),self.__checkIntValue("DDAP",data),self.__checkIntValue("RADV",data),self.__checkIntValue("RAPR",data),self.__checkIntValue("RARC",data),self.__checkFloatValue("RADR",data),self.__checkFloatValue("RMCV",data,4),self.__checkFloatValue("RACV",data,4),self.__checkFloatValue("RABA",data,4),self.__checkIntValue("RTYP",data),self.__checkIntValue("STYP",data)))

      #my_list.extend([self.__site_id,self.__network_id,mydate,patterntype,self.__checkFloatValue("AMP1",data,4),self.__checkFloatValue("AMP2",data,4),self.__checkFloatValue("PH13",data,4),self.__checkFloatValue("PH23",data,4),self.__checkFloatValue("CPH1",data,4),self.__checkFloatValue("CPH2",data,4),self.__checkFloatValue("SNF1",data,4),self.__checkFloatValue("SNF2",data,4),self.__checkFloatValue("SNF3",data,4),self.__checkFloatValue("SSN1",data),self.__checkFloatValue("SSN2",data),self.__checkFloatValue("SSN3",data),self.__checkIntValue("DGRC",data),self.__checkIntValue("DOPV",data),self.__checkIntValue("DDAP",data),self.__checkIntValue("RADV",data),self.__checkIntValue("RAPR",data),self.__checkIntValue("RARC",data),self.__checkFloatValue("RADR",data),self.__checkFloatValue("RMCV",data,4),self.__checkFloatValue("RACV",data,4),self.__checkFloatValue("RABA",data,4),self.__checkIntValue("RTYP",data),self.__checkIntValue("STYP",data)])
      #my_lists.append(my_list)

    return my_lists 
  # end  __getRadialDiagnosticsSQLInsert

  def getRadialMetaSQLInsert(self):
    """ 
    Returns the sql used to insert radialfile data into the database

    @return str insert SQL
    """
    my_lists = []
    data = self.getRadialFileMeta()
    if not data: return data

    # Get file extension
    extension = os.path.splitext(self.filename)[1].lstrip(".")

    self.__checkStationNetworkID()

    # Get pattern type
    patterntype = self.getPatternType()
    finaldir = "{}{}/{}/{}".format(self.config['directories']['node_final_dir'],self.__getNetworkName(),self.__getStationName(),self.__getYearMonth())
    #my_list = []
    my_lists.append("({},{},{},'{}','{}',{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},'{}','{}',{},{},{},{},{},{},{},{},{},{},'{}')".format( self.__site_id,self.__network_id,self.__checkFloatValue("time",data),extension,patterntype,self.__checkFloatValue("lat",data,6),self.__checkFloatValue("lon",data,6),self.__checkFloatValue("cfreq",data,11),self.__checkFloatValue("range_res",data,4),self.__checkFloatValue("ref_bearing",data,4),self.__checkFloatValue("nrads",data),self.__checkFloatValue("dres",data,8),self.__checkValue("manufacturer",data),self.__checkFloatValue("xmit_sweep_rate",data,8),self.__checkFloatValue("xmit_bandwidth",data,8),self.__checkFloatValue("max_curr_lim",data,8),self.__checkFloatValue("min_rad_vect_pts",data),self.__checkFloatValue("loop1_amp_corr",data),self.__checkFloatValue("loop2_amp_corr",data),self.__checkFloatValue("loop1_phase_corr",data),self.__checkFloatValue("loop2_phase_corr",data),self.__checkFloatValue("bragg_smooth_pts",data),self.__checkFloatValue("rad_bragg_peak_dropoff",data),self.__checkFloatValue("second_order_bragg",data),self.__checkFloatValue("rad_bragg_peak_null",data),self.__checkFloatValue("rad_bragg_noise_thr",data),self.__checkFloatValue("music_param_01",data),self.__checkFloatValue("music_param_02",data),self.__checkFloatValue("music_param_03",data),self.__checkValue("ellip",data),self.__checkFloatValue("earth_radius",data,15),self.__checkFloatValue("ellip_flatten",data,9),self.__checkValue("rad_merger_ver",data),self.__checkValue("spec2rad_ver",data),self.__checkValue("ctf_ver",data),self.__checkValue("lluvspec_ver",data),self.__checkValue("geod_ver",data),self.__checkValue("rad_slider_ver",data),self.__checkValue("rad_archiver_ver",data),self.__checkFloatValue("patt_date",data),self.__checkFloatValue("patt_res",data),self.__checkFloatValue("patt_smooth",data),self.__checkFloatValue("spec_range_cells",data),self.__checkFloatValue("spec_doppler_cells",data),self.__checkValue("curr_ver",data),self.__checkValue("codartools_ver",data),self.__checkFloatValue("first_order_calc",data),self.__checkValue("lluv_tblsubtype",data),self.__checkValue("proc_by",data),self.__checkFloatValue("merge_method",data),self.__checkFloatValue("patt_method",data),finaldir,os.path.basename(self.filename),self.getModificationTime(),self.__checkFloatValue("sampling_period_hrs",data,4),self.__checkFloatValue("nmerge_rads",data),self.__checkFloatValue("proc_time",data),self.__checkFloatValue("range_bin_start",data),self.__checkFloatValue("range_bin_end",data),self.__checkFloatValue("loop1_amp_calc",data),self.__checkFloatValue("loop2_amp_calc",data),self.__checkFloatValue("loop1_phase_calc",data),self.__checkFloatValue("loop2_phase_calc",data),datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")))
    #my_lists.append("({},{},{},'{}','{}',{},{},{},{},{},{},{},'{}',{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},'{}',{},{},'{}','{}','{}','{}','{}','{}','{}','{}',{},{},{},{},'{}','{}',{},'{}',{},{},{},'{}','{}',{},{},{},{},{},{},{},{},{},{},'{}')".format( self.__site_id,self.__network_id,self.__checkFloatValue("time",data),extension,patterntype,self.__checkFloatValue("lat",data,6),self.__checkFloatValue("lon",data,6),self.__checkFloatValue("cfreq",data,11),self.__checkFloatValue("range_res",data,4),self.__checkFloatValue("ref_bearing",data,4),self.__checkFloatValue("nrads",data),self.__checkFloatValue("dres",data,8),self.__checkValue("manufacturer",data),self.__checkFloatValue("xmit_sweep_rate",data,8),self.__checkFloatValue("xmit_bandwidth",data,8),self.__checkFloatValue("max_curr_lim",data,8),self.__checkFloatValue("min_rad_vect_pts",data),self.__checkFloatValue("loop1_amp_corr",data),self.__checkFloatValue("loop2_amp_corr",data),self.__checkFloatValue("loop1_phase_corr",data),self.__checkFloatValue("loop2_phase_corr",data),self.__checkFloatValue("bragg_smooth_pts",data),self.__checkFloatValue("rad_bragg_peak_dropoff",data),self.__checkFloatValue("second_order_bragg",data),self.__checkFloatValue("rad_bragg_peak_null",data),self.__checkFloatValue("rad_bragg_noise_thr",data),self.__checkFloatValue("music_param_01",data),self.__checkFloatValue("music_param_02",data),self.__checkFloatValue("music_param_03",data),self.__checkValue("ellip",data),self.__checkFloatValue("earth_radius",data,15),self.__checkFloatValue("ellip_flatten",data,18),self.__checkValue("rad_merger_ver",data),self.__checkValue("spec2rad_ver",data),self.__checkValue("ctf_ver",data),self.__checkValue("lluvspec_ver",data),self.__checkValue("geod_ver",data),self.__checkValue("rad_slider_ver",data),self.__checkValue("rad_archiver_ver",data),self.__checkFloatValue("patt_date",data),self.__checkFloatValue("patt_res",data),self.__checkFloatValue("patt_smooth",data),self.__checkFloatValue("spec_range_cells",data),self.__checkFloatValue("spec_doppler_cells",data),self.__checkValue("curr_ver",data),self.__checkValue("codartools_ver",data),self.__checkFloatValue("first_order_calc",data),self.__checkValue("lluv_tblsubtype",data),self.__checkValue("proc_by",data),self.__checkFloatValue("merge_method",data),self.__checkFloatValue("patt_method",data),finaldir,os.path.basename(self.filename),os.path.getmtime(self.filename),self.__checkFloatValue("sampling_period_hrs",data,4),self.__checkFloatValue("nmerge_rads",data),self.__checkFloatValue("proc_time",data),self.__checkFloatValue("range_bin_start",data),self.__checkFloatValue("range_bin_end",data),self.__checkFloatValue("loop1_amp_calc",data),self.__checkFloatValue("loop2_amp_calc",data),self.__checkFloatValue("loop1_phase_calc",data),self.__checkFloatValue("loop2_phase_calc",data),datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")))

    #my_list.extend([ self.__site_id,self.__network_id,self.__checkFloatValue("time",data),extension,patterntype,self.__checkFloatValue("lat",data,6),self.__checkFloatValue("lon",data,6),self.__checkFloatValue("cfreq",data,11),self.__checkFloatValue("range_res",data,4),self.__checkFloatValue("ref_bearing",data,4),self.__checkFloatValue("nrads",data),self.__checkFloatValue("dres",data,8),self.__checkValue("manufacturer",data),self.__checkFloatValue("xmit_sweep_rate",data,8),self.__checkFloatValue("xmit_bandwidth",data,8),self.__checkFloatValue("max_curr_lim",data,8),self.__checkFloatValue("min_rad_vect_pts",data),self.__checkFloatValue("loop1_amp_corr",data),self.__checkFloatValue("loop2_amp_corr",data),self.__checkFloatValue("loop1_phase_corr",data),self.__checkFloatValue("loop2_phase_corr",data),self.__checkFloatValue("bragg_smooth_pts",data),self.__checkFloatValue("rad_bragg_peak_dropoff",data),self.__checkFloatValue("second_order_bragg",data),self.__checkFloatValue("rad_bragg_peak_null",data),self.__checkFloatValue("rad_bragg_noise_thr",data),self.__checkFloatValue("music_param_01",data),self.__checkFloatValue("music_param_02",data),self.__checkFloatValue("music_param_03",data),self.__checkValue("ellip",data),self.__checkFloatValue("earth_radius",data,15),self.__checkFloatValue("ellip_flatten",data,18),self.__checkValue("rad_merger_ver",data),self.__checkValue("spec2rad_ver",data),self.__checkValue("ctf_ver",data),self.__checkValue("lluvspec_ver",data),self.__checkValue("geod_ver",data),self.__checkValue("rad_slider_ver",data),self.__checkValue("rad_archiver_ver",data),self.__checkFloatValue("patt_date",data),self.__checkFloatValue("patt_res",data),self.__checkFloatValue("patt_smooth",data),self.__checkFloatValue("spec_range_cells",data),self.__checkFloatValue("spec_doppler_cells",data),self.__checkValue("curr_ver",data),self.__checkValue("codartools_ver",data),self.__checkFloatValue("first_order_calc",data),self.__checkValue("lluv_tblsubtype",data),self.__checkValue("proc_by",data),self.__checkFloatValue("merge_method",data),self.__checkFloatValue("patt_method",data),finaldir,os.path.basename(self.filename),os.path.getmtime(self.filename),self.__checkFloatValue("sampling_period_hrs",data,4),self.__checkFloatValue("nmerge_rads",data),self.__checkFloatValue("proc_time",data),self.__checkFloatValue("range_bin_start",data),self.__checkFloatValue("range_bin_end",data),self.__checkFloatValue("loop1_amp_calc",data),self.__checkFloatValue("loop2_amp_calc",data),self.__checkFloatValue("loop1_phase_calc",data),self.__checkFloatValue("loop2_phase_calc",data),datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")])
    
    #my_lists.append(my_list)
    return my_lists 
  # end  __getRadialMetaSQLInsert

  def insertIntoDB(self):
    """
    Inserts the radial file into the database

    @return True/False depending on whether it works or not
    """
    # Get site_id and network_id
    site_networkID = self.getStationNetworkID()
    self.__site_id = site_networkID["site_id"]
    self.__network_id = site_networkID["network_id"]
 
    # Hardware diagnostics
    logging.debug("insertIntoDB(): Getting hardware diagnostics data")
    hd = self.getHardwareDiagnosticsSQLInsert()
    if hd:
      s = ","
      sql = "replace into hardwarediag values {}".format(s.join(hd))
      try:
        cur = self.db.cursor()
        cur.execute(sql)
        #cur = self.executeQuery(sql)
        self.db.commit()
      except Exception as e:
        logging.error("Unable to insert hardwarediag data: {}".format(e))
        return False

    # Radial Diagnostics
    logging.debug("insertIntoDB(): Getting radial diagnostics data")
    rd = self.getRadialDiagnosticsSQLInsert()
    if rd:
      s = ","
      sql = "replace into radialdiag values {}".format(s.join(rd))
      #sql = "replace into radialdiag values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
      try:
        cur = self.db.cursor()
        cur.execute(sql)
        #cur = self.executeQuery(sql)
        self.db.commit()
      except Exception as e:
        logging.error("Unable to insert radialdiag data: {}".format(e))
        return False

    # get radial file meta 
    logging.debug("insertIntoDB(): Getting radial meta data")
    results = self.getRadialMetaSQLInsert()
    if results:
      s = ","
      sql = "replace into radialfiles values {}".format(s.join(results)) 
      try:
        cur = self.db.cursor()
        cur.execute(sql)
        #cur = self.executeQuery(sql)
        self.db.commit()
      except Exception as e:
        logging.error("Unable to insert radialfiles data: {}".format(e))
        return False
 
    self.__closeDBConnection()

    return True
  # End insertIntoDB

  def __checkValue(self,variable,data):
    """
    Check to see if a key is in a dictionary and if so, return the value or a default value
    @param - variable- key variable to check for
    @param - data - dictionary containing values
    @return - empty string or value
    """
    if variable in data:
      return "'{}'".format(data[ variable ])
    else:
      return "DEFAULT"
  # End __checkValue
 
  def __checkFloatValue(self, variable, data,precision=2):
    """
    Check an key in a dictionary and return as float if it exists
    @param - variable- key variable to check for
    @param - data - dictionary containing values
    @param - precision - number of decimal places (default 2) 
    @return - None or float value
    """
    val = self.__checkValue(variable, data)
    if "DEFAULT" in val:
      return 'DEFAULT' 
    else:
      try:
        myval = "{:.{}f}".format(float(data[ variable ]),precision)
      except Exception as e:
        logging.error("checkFloatValue(): Error converting {} to float.".format(data[ variable]))
        return None
      return myval
  # end __checkFloatValue

  def __checkIntValue(self, variable, data):
    """
    Check an key in a dictionary and return as int if it exists
    @param - variable- key variable to check for
    @param - data - dictionary containing values
    @return - None or int value
    """
    val = self.__checkValue(variable, data)
    if "DEFAULT" in val:
      return 'DEFAULT' 
    else:
      try:
        myval = int(float(data[ variable ]))
      except Exception as e:
        logging.error("checkIntValue(): Error converting {} to int.".format(data[ variable]))
        return None
      return int(float(data[ variable ]))
  # end __checkIntValue

  def setIniFile(self,inifile):
    """
    Sets and loads the ini file 
    @param str filename
    @return boolean true if successful
    """
    try:
      self.config.read_file(open(inifile))
    except FileNotFoundError:
      logging.error("Unable to read ini file {}".format(inifile))

    # make sure the required keys and sections are in the ini file
    if (not self.config.has_option("data_database","host") or
        not self.config.has_option("data_database","user") or
        not self.config.has_option("data_database","passwd") or
        not self.config.has_option("data_database","db")):
      logging.error("insertIntoDB(): Ini file is missing section data_database and/or keys host, user, passwd, db")
      return False
      #sys.exit()

    # connect to my database
    try:
      if self.config.has_option("data_database","ssl_ca"):
        self.db = pymysql.connect(user=self.config['data_database']['user'], 
                       passwd=self.config['data_database']['passwd'], 
                       host=self.config['data_database']['host'], 
                       db=self.config['data_database']['db'],
                       port=int(self.config['data_database']['port']),
                       ssl={'ssl':{'ca': self.config['data_database']['ssl_ca'],
                                   'key' : self.config['data_database']['ssl_client_key'],
                                   'cert' : self.config['data_database']['ssl_client_cert'] } },
                       cursorclass=pymysql.cursors.DictCursor)      
      else:
        self.db = pymysql.connect(user=self.config['data_database']['user'], 
                       passwd=self.config['data_database']['passwd'], 
                       host=self.config['data_database']['host'], 
                       db=self.config['data_database']['db'],
                       port=int(self.config['data_database']['port']),
                       cursorclass=pymysql.cursors.DictCursor)      
    except Exception as e:
      logging.error("setIniFile(): Unable to connect to MySQL database: "+self.config['data_database']['db'] + ". " + str(e))
      return False
      #sys.exit()
    return True
  # end setIniFile

  def getStationNetworkID(self):
    """
    Gets the station and network id from the database
    @return dict site_id, network_id
    """
    query = "SELECT s.site_id,s.network_id FROM site s LEFT JOIN network n on s.network_id=n.network_id WHERE s.sta='{}' and n.net='{}'".format(self.__getStationName(), self.__getNetworkName())
    mydata = {}
    logging.debug(query) 
    mydata = self.executeQuery(query).fetchone()
    return mydata
  # End getStationNetworkID

  def executeQuery(self,sql):
    """
    Execute a SQL query
    @param str - sql query
    @return cursor object
    """
    try:
      cursor = self.db.cursor()
      cursor.execute(sql)
      return cursor
    except Exception as e:
      logging.error("executeQuery(): Unable to execute query - {} - {}".format(sql,e))
      #self.__closeDBConnection()

  def executeManyQuery(self,sql,data=None):
    """
    Execute many a SQL query
    @param str - sql query
    @param data - list containing values
    @return cursor object
    """
    try:
      cursor = self.db.cursor()
      if data == None:
        cursor.executemany(sql)
      else:
        cursor.executemany(sql,data)
      return cursor
    except Exception as e:
      logging.error("executeManyQuery(): Unable to execute query - {}. {} ".format(sql,e))
      #self.__closeDBConnection()
  # End executeManyQuery

  def __closeDBConnection(self):
    """ 
    Close my database connection and exit
    """
    self.db.close()
