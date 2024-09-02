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

class WaveFile:
  """
  This class handles wave files.

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
    2022-12-06 - Forking this over from RadialFile
    2023-01-18 - Updating for wavefile stuff
    2023-02-18 - Bug: checkIntValue() convert value to float before int.  String float will give an error with just int
    2023-04-04 - checkValue return '-' instead of 'DEFAULT'.  Added more columns into insertintodb
    2023-08-18 - Bug: added WaveSecondOrderMethod check
  """
  
  def __init__(self,filename):
    """
    The constructor for the WaveFile class.
    
    @params:
      filename (str) - The path and filename of the wave file.
    """
    self.filename = filename
    self.modificationTime = self.getModificationTime()
    self.config = configparser.ConfigParser()

  def getModificationTime(self):
    """
    Returns the modification time of the wave file
    
    Returns:
      epoch timestamp
    """
    return round(os.path.getmtime(self.filename),5)
  # End getModificationTime  
 
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

  def validWAVLWVM9Table(self):
    """
    Checks if the WAVL WVM9 table type is valid.
    
    Returns: True/False
    """
    pattern = "^\s*%TableType:\s+WAVL\s+WVM9"
    result = grep( pattern, self.filename )
    if not result:
      logging.error("Table type WAVL WVM9 not defined")
      return False

    pattern = "^\s*[^%]"
    result = grep( pattern, self.filename )
    if not result:
      logging.error("No wave data found")
      return False

    result = retrieveBetweenTwoPatterns("%TableType","%TableEnd", self.filename)
    if not result:
      logging.error("Wave tables not found")
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
    Checks if the wave file is valid. Performs all of the valid* functions.
    
    Returns: True/False
    """
    if not self.validCTFdata(): return False
    if not self.validSiteMetadata(): return False
    if not self.validTimeStampMetadata(): return False
    if not self.validTimeZoneMetadata(): return False
    if not self.validLatLon(): return False
    if not self.validWAVLWVM9Table(): return False

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
            #logging.warning("invalid entry, %s",line)
          if "nan" in line:
            line = line.replace('nan','DEFAULT')
            #logging.warning("invalid entry, %s",line)
          if "999.00" in line:
            line = line.replace('999.00','DEFAULT')
            #logging.warning("invalid entry, %s",line)
          if "-999.00" in line:
            line = line.replace('-999.00','DEFAULT')
            #logging.warning("invalid entry, %s",line)
          if "1080.0" in line:
            line = line.replace('1080.0','DEFAULT')
            #logging.warning("invalid entry, %s",line)

          data = line.split( None );
          # Skip anything that isn't our data
          if not is_number(data[0]): continue
          data = dict(zip(headers,data))

          # Get the date only for wave diagnostics and hardware diag.  lluv data doesn't have dates
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

  def getWAVLData(self):
    """
    Gets the data from the 'WAVL WVM9' table.  
  
    @return array Associative array with keys being the column type (TIME, AMP1...) and values being the data 
    """
    return self.__getTableData("%TableType: WAVL WVM9","%TableEnd:")
  # End  getLLUVData

  def getProcessInfo(self):
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
    
    return data
  # End  getProcessInfo

  def getWaveMeta(self,sql=True):
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
      if line == "%%": continue
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
      if key== "Origin":
        dataSQL["lat"] = '%.7f'%(float(arr[0]))
        dataSQL["lon"] = '%.7f'%(float(arr[1]))
      elif key== "TimeStamp":
        dataSQL["time"] = datetime(int(arr[0]),int(arr[1]),int(arr[2]),int(arr[3]),int(arr[4]),int(arr[5]),tzinfo=timezone.utc).timestamp() 
      elif key=="TimeCoverage":
        dataSQL[key] = value
      elif key=="CoastlineSector":
        dataSQL[key] = arr[0]+" " +arr[1]
      elif key=="WaveBearingLimits":
        dataSQL[key] = arr[0]+" " +arr[1]
      elif key=="WaveUseInnerBragg":
        dataSQL[key] = arr[0]
      elif key=="WavesFollowTheWind":
        dataSQL[key] = arr[0]
      elif key=="WaveSecondOrderMethod":
        dataSQL[key] = arr[0]
      elif key=="WaveMergeMethod":
        dataSQL[key] = arr[0]
      elif key=="WaveReductionMethod":
        dataSQL[key] = arr[0]
      else:
        dataSQL[key] = value

    # end for key, value in data
    return dataSQL;
  # End function getWaveMeta

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
    pattern = re.compile("WVLM.+?([a-zA-Z0-9]{2,25})_([a-zA-Z0-9]{3,6})_(\d{4})_(\d{2})_(\d{2})_(\d{4}).(.*)")
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
    
  def insertIntoDB(self):
    """
    Inserts the wave file into the database

    @return True/False depending on whether it works or not
    """
    firstwavl = True

    # Get site_id and network_id
    site_networkID = self.getStationNetworkID()
    self.__site_id = site_networkID["site_id"]
    self.__network_id = site_networkID["network_id"]
 
    # First get the WAVL data
    wavldatas = self.getWAVLData()
    processinfo = self.getProcessInfo()
    metadata = self.getWaveMeta()
    
    # Foreach wavldata (last to first)
    # I only want to use metadata and processinfo if this is the last entry in wavldata
    for wavldata in reversed(wavldatas) :
      # Figure out the datetime for the line
      mytime = datetime(int(wavldata['TYRS']),int(wavldata['TMON']),int(wavldata['TDAY']),int(wavldata['THRS']),int(wavldata['TMIN']),int(wavldata['TSEC']),tzinfo=timezone.utc).timestamp() 
  
      if firstwavl == True:
        # make my sql insert statement
        myinsertvalues = "({},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{})".\
          format( self.__site_id,\
                  self.__network_id,\
                  mytime,\
                  self.__checkValue("CTF",metadata),\
                  self.__checkValue("FileType",metadata),\
                  self.__checkValue("UUID",metadata),\
                  self.__checkValue("Manufacturer",metadata),\
                  self.__checkValue("TimeMarks",metadata),\
                  self.__checkValue("TimeZone",metadata),\
                  self.__checkFloatValue("lat",metadata,6),\
                  self.__checkFloatValue("lon",metadata,6),\
                  self.__checkValue("TimeCoverage",metadata),\
                  self.__checkFloatValue("RangeResolutionKMeters",metadata),\
                  self.__checkFloatValue("AntennaBearing",metadata,1),\
                  self.__checkIntValue("RangeCells",metadata),\
                  self.__checkIntValue("DopplerCells",metadata),\
                  self.__checkFloatValue("TransmitCenterFreqMHz",metadata,8),\
                  self.__checkFloatValue("TransmitBandwidthKHz",metadata,8),\
                  self.__checkFloatValue("TransmitSweepRateHz",metadata,8),\
                  self.__checkValue("CoastlineSector",metadata),\
                  self.__checkIntValue("CurrentVelocityLimit",metadata),\
                  self.__checkIntValue("BraggSmoothingPoints",metadata),\
                  self.__checkIntValue("BraggHasSecondOrder",metadata),\
                  self.__checkFloatValue("WaveBraggNoiseThreshold",metadata),\
                  self.__checkFloatValue("WaveBraggPeakDropOff",metadata),\
                  self.__checkFloatValue("WaveBraggPeakNull",metadata),\
                  self.__checkFloatValue("MaximumWavePeriod",metadata),\
                  self.__checkValue("WaveBearingLimits",metadata),\
                  self.__checkIntValue("WaveUseInnerBragg",metadata),\
                  self.__checkIntValue("WaveSecondOrderMethod",metadata),\
                  self.__checkIntValue("WavesFollowTheWind",metadata),\
                  self.__checkFloatValue("WaveSaturationRatio",metadata),\
                  self.__checkFloatValue("WaveHeightLimit",metadata),\
                  self.__checkFloatValue("WavePeriodSetLimit",metadata),\
                  self.__checkValue("PatternUUID",metadata),\
                  self.__checkIntValue("WaveMergeMethod",metadata),\
                  self.__checkIntValue("WaveReductionMethod",metadata),\
                  self.__checkIntValue("WaveMinDopplerPoints",metadata),\
                  self.__checkIntValue("WaveMinVectors",metadata),\
                  self.__checkFloatValue("WaveMaximumWaveHeight",metadata),\
                  self.__checkFloatValue("WaveMaximumWavePeriodChange",metadata),\
                  self.__checkFloatValue("WaveOutlierLowerPercentage",metadata),\
                  self.__checkFloatValue("WaveOutlierUpperPercentage",metadata),\
                  self.__checkFloatValue("MWHT",wavldata),\
                  self.__checkFloatValue("MWPD",wavldata),\
                  self.__checkFloatValue("WAVB",wavldata),\
                  self.__checkFloatValue("WNDB",wavldata),\
                  self.__checkFloatValue("PMWH",wavldata),\
                  self.__checkIntValue("ACNT",wavldata),\
                  self.__checkFloatValue("DIST",wavldata),\
                  self.__checkFloatValue("LOND",wavldata),\
                  self.__checkFloatValue("LATD",wavldata),\
                  self.__checkIntValue("RCLL",wavldata),\
                  self.__checkIntValue("WDPT",wavldata),\
                  self.__checkIntValue("MTHD",wavldata),\
                  self.__checkIntValue("FLAG",wavldata),\
                  self.__checkIntValue("WHNM",wavldata),\
                  self.__checkFloatValue("WHSD",wavldata),\
                  self.__checkValue("ProcessedTimeStamp",processinfo),\
                  self.__checkValue("WaveModelFilter",processinfo),\
                  self.__checkValue("SpectraToWavesModel",processinfo),\
                  self.__checkValue("WaveModelForFive",processinfo),\
                  self.__checkValue("WaveModelArchiver",processinfo),\
                  self.__checkValue("AnalyzeSpectra",processinfo) )
          
        firstwavl = False
      else:
        myinsertvalues = "({},{},{},{},{},{},{},{},{},{},{},DEFAULT,DEFAULT,DEFAULT,DEFAULT,DEFAULT,DEFAULT,DEFAULT,DEFAULT,DEFAULT,DEFAULT,DEFAULT,DEFAULT,DEFAULT,DEFAULT,DEFAULT,DEFAULT,DEFAULT,DEFAULT,DEFAULT,DEFAULT,DEFAULT,DEFAULT,DEFAULT,DEFAULT,DEFAULT, DEFAULT, DEFAULT,DEFAULT,DEFAULT,DEFAULT,DEFAULT,DEFAULT,{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},DEFAULT,DEFAULT,DEFAULT,DEFAULT,DEFAULT,DEFAULT)".\
          format( self.__site_id,\
                  self.__network_id,\
                  mytime,\
                  self.__checkValue("CTF",metadata),\
                  self.__checkValue("FileType",metadata),\
                  self.__checkValue("UUID",metadata),\
                  self.__checkValue("Manufacturer",metadata),\
                  self.__checkValue("TimeMarks",metadata),\
                  self.__checkValue("TimeZone",metadata),\
                  self.__checkFloatValue("lat",metadata,6),\
                  self.__checkFloatValue("lon",metadata,6),\
                  self.__checkFloatValue("MWHT",wavldata),\
                  self.__checkFloatValue("MWPD",wavldata),\
                  self.__checkFloatValue("WAVB",wavldata),\
                  self.__checkFloatValue("WNDB",wavldata),\
                  self.__checkFloatValue("PMWH",wavldata),\
                  self.__checkIntValue("ACNT",wavldata),\
                  self.__checkFloatValue("DIST",wavldata),\
                  self.__checkFloatValue("LOND",wavldata),\
                  self.__checkFloatValue("LATD",wavldata),\
                  self.__checkIntValue("RCLL",wavldata),\
                  self.__checkIntValue("WDPT",wavldata),\
                  self.__checkIntValue("MTHD",wavldata),\
                  self.__checkIntValue("FLAG",wavldata),\
                  self.__checkIntValue("WHNM",wavldata),\
                  self.__checkFloatValue("WHSD",wavldata))

      if myinsertvalues:
        s = ","
        sql = "INSERT into wavefiles (`site_id`, `network_id`, `time`, `CTF`, `FileType`, `UUID`, `Manufacturer`, `TimeMarks`, `TimeZone`, `lat`, `lon`, `TimeCoverage`, `RangeResolutionKMeters`, `AntennaBearing`, `RangeCells`, `DopplerCells`, `TransmitCenterFreqMHz`, `TransmitBandwidthKHz`, `TransmitSweepRateHz`, `CoastlineSector`, `CurrentVelocityLimit`, `BraggSmoothingPoints`, `BraggHasSecondOrder`, `WaveBraggNoiseThreshold`, `WaveBraggPeakDropOff`, `WaveBraggPeakNull`, `MaximumWavePeriod`, `WaveBearingLimits`, `WaveUseInnerBragg`, `WaveSecondOrderMethod`, `WavesFollowTheWind`, `WaveSaturationRatio`, `WaveHeightLimit`, `WavePeriodSetLimit`, `PatternUUID`, `WaveMergeMethod`, `WaveReductionMethod`, `WaveMinDopplerPoints`, `WaveMinVectors`, `WaveMaximumWaveHeight`, `WaveMaximumWavePeriodChange`, `WaveOutlierLowerPercentage`, `WaveOutlierUpperPercentage`, `MWHT`, `MWPD`, `WAVB`, `WNDB`, `PMWH`, `ACNT`, `DIST`, `LOND`, `LATD`, `RCLL`, `WDPT`, `MTHD`, `FLAG`, `WHNM`, `WHSD`, `ProcessedTimeStamp`, `WaveModelFilter`, `SpectraToWavesModel`, `WaveModelForFive`, `WaveModelArchiver`, `AnalyzeSpectra`) values {}".format(myinsertvalues) 
        try:
          cur = self.db.cursor()
          cur.execute(sql)
          self.db.commit()
        except Exception as e:
          # Trying to insert values if it's already in the DB, skip it and move on
          if e.args[0] == 1062:
            continue
          
          logging.error("Unable to insert wavefiles data: {}".format(e))
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
      return "'-'"
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
    if val == "'-'" or val=="-" or val=="nan" or val=="'DEFAULT'" or val=="DEFAULT":
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
    if val == "'-'" or val=="-" or val=="nan" or val=="'DEFAULT'" or val=="DEFAULT":
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
