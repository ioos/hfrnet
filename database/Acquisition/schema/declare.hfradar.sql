-- MySQL dump 10.13  Distrib 8.0.33, for Linux (x86_64)
--
-- Host: localhost    Database: hfradar
-- ------------------------------------------------------
-- Server version	8.0.33

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `disks`
--

DROP TABLE IF EXISTS `disks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `disks` (
  `site_id` mediumint unsigned NOT NULL,
  `time` decimal(17,5) NOT NULL,
  `filesystem` varchar(100) NOT NULL DEFAULT 'unknown',
  `1M-blocks` int unsigned DEFAULT NULL,
  `used` int unsigned DEFAULT NULL,
  `available` int unsigned DEFAULT NULL,
  `use_percent` tinyint unsigned DEFAULT NULL,
  `mounted_on` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`site_id`,`filesystem`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `geoLocations`
--

DROP TABLE IF EXISTS `geoLocations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `geoLocations` (
  `gID` int NOT NULL AUTO_INCREMENT,
  `gCityFormal` varchar(30) DEFAULT NULL,
  `gRegion` varchar(10) DEFAULT NULL,
  `gCountry` char(2) DEFAULT NULL,
  `gLat` decimal(12,8) NOT NULL DEFAULT '0.00000000',
  `gLon` decimal(12,8) NOT NULL DEFAULT '0.00000000',
  PRIMARY KEY (`gID`)
) ENGINE=InnoDB AUTO_INCREMENT=2989417 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hardwarediag`
--

DROP TABLE IF EXISTS `hardwarediag`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `hardwarediag` (
  `site_id` mediumint unsigned NOT NULL,
  `network_id` mediumint unsigned NOT NULL,
  `time` decimal(17,5) NOT NULL,
  `receiver_chassis_tmp` int DEFAULT '-9999',
  `awg_tmp` int DEFAULT '-9999',
  `transmit_trip` char(10) DEFAULT '-',
  `awg_run_time` int DEFAULT '-9999',
  `receiver_supply_p24vdc` decimal(15,2) DEFAULT '-9999.00',
  `receiver_supply_p5vdc` decimal(15,2) DEFAULT '-9999.00',
  `receiver_supply_n5vdc` decimal(15,2) DEFAULT '-9999.00',
  `receiver_supply_p12vdc` decimal(15,2) DEFAULT '-9999.00',
  `xmit_chassis_tmp` int DEFAULT '-9999',
  `xmit_amp_tmp` int DEFAULT '-9999',
  `xmit_fwd_pwr` int DEFAULT '-9999',
  `xmit_ref_pwr` int DEFAULT '-9999',
  `xmit_supply_p28vdc` decimal(15,2) DEFAULT '-9999.00',
  `xmit_supply_p5vdc` decimal(15,2) DEFAULT '-9999.00',
  `gps_receive_mode` int DEFAULT '-9999',
  `gps_discipline_mode` int DEFAULT '-9999',
  `npll_unlock` int DEFAULT '-9999',
  `receiver_hires_tmp` decimal(15,2) DEFAULT '-9999.00',
  `receiver_humidity` int DEFAULT '-9999',
  `vdc_draw` decimal(15,2) DEFAULT '-9999.00',
  `cpu_runtime` decimal(17,2) DEFAULT '-9999.00',
  PRIMARY KEY (`site_id`,`network_id`,`time`),
  CONSTRAINT `fk_hardwarediag_site1` FOREIGN KEY (`site_id`, `network_id`) REFERENCES `site` (`site_id`, `network_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`rt`@`hfrnet-cs.ucsd.edu`*/ /*!50003 TRIGGER `hardwarediag_AINS` AFTER INSERT ON `hardwarediag` FOR EACH ROW begin
IF ((select time from latest_hardwarediag where site_id = NEW.site_id and network_id = NEW.network_id) < NEW.time) OR isnull((select time from latest_hardwarediag where site_id = NEW.site_id and network_id = NEW.network_id)) then
  INSERT INTO latest_hardwarediag VALUES (NEW.network_id,NEW.site_id,NEW.time)
    ON DUPLICATE KEY UPDATE time=NEW.time;
end if;
end */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `latest_hardwarediag`
--

DROP TABLE IF EXISTS `latest_hardwarediag`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `latest_hardwarediag` (
  `network_id` mediumint unsigned NOT NULL,
  `site_id` mediumint unsigned NOT NULL,
  `time` decimal(17,5) NOT NULL,
  PRIMARY KEY (`network_id`,`site_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `latest_radialdiag`
--

DROP TABLE IF EXISTS `latest_radialdiag`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `latest_radialdiag` (
  `network_id` mediumint NOT NULL,
  `site_id` mediumint NOT NULL,
  `time` decimal(17,5) NOT NULL,
  `patterntype` enum('i','m') NOT NULL DEFAULT 'm',
  PRIMARY KEY (`network_id`,`site_id`,`patterntype`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `latest_radialfiles`
--

DROP TABLE IF EXISTS `latest_radialfiles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `latest_radialfiles` (
  `network_id` mediumint NOT NULL,
  `site_id` mediumint NOT NULL,
  `time` decimal(17,5) NOT NULL,
  `patterntype` enum('i','m') NOT NULL DEFAULT 'm',
  PRIMARY KEY (`network_id`,`site_id`,`patterntype`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `network`
--

DROP TABLE IF EXISTS `network`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `network` (
  `network_id` mediumint unsigned NOT NULL AUTO_INCREMENT,
  `net` char(20) NOT NULL,
  `netname` char(80) DEFAULT NULL,
  `regional_association` varchar(10) DEFAULT '',
  PRIMARY KEY (`network_id`),
  UNIQUE KEY `network_id_UNIQUE` (`network_id`),
  UNIQUE KEY `net_UNIQUE` (`net`)
) ENGINE=InnoDB AUTO_INCREMENT=53 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `radialdiag`
--

DROP TABLE IF EXISTS `radialdiag`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `radialdiag` (
  `site_id` mediumint unsigned NOT NULL,
  `network_id` mediumint unsigned NOT NULL,
  `time` decimal(17,5) NOT NULL,
  `patterntype` enum('i','m') NOT NULL DEFAULT 'm',
  `loop1_amp_calc` decimal(15,4) DEFAULT '-9999.0000',
  `loop2_amp_calc` decimal(15,4) DEFAULT '-9999.0000',
  `loop1_phase_calc` decimal(15,4) DEFAULT '-9999.0000',
  `loop2_phase_calc` decimal(15,4) DEFAULT '-9999.0000',
  `loop1_phase_corr` decimal(10,4) DEFAULT '-9999.0000',
  `loop2_phase_corr` decimal(10,4) DEFAULT '-9999.0000',
  `loop1_css_noisefloor` decimal(15,4) DEFAULT '-9999.0000',
  `loop2_css_noisefloor` decimal(15,4) DEFAULT '-9999.0000',
  `mono_css_noisefloor` decimal(15,4) DEFAULT '-9999.0000',
  `loop1_css_snr` decimal(15,2) DEFAULT '-9999.00',
  `loop2_css_snr` decimal(15,2) DEFAULT '-9999.00',
  `mono_css_snr` decimal(15,2) DEFAULT '-9999.00',
  `diag_range_cell` int DEFAULT '-9999',
  `valid_doppler_cells` int DEFAULT '-9999',
  `dual_angle_pcnt` int DEFAULT '-9999',
  `rad_vect_count` int DEFAULT '-9999',
  `avg_rads_per_range` int DEFAULT '-9999',
  `nrange_proc` int DEFAULT '-9999',
  `rad_range` decimal(15,2) DEFAULT '-9999.00',
  `max_rad_spd` decimal(15,4) DEFAULT '-9999.0000',
  `avg_rad_spd` decimal(15,4) DEFAULT '-9999.0000',
  `avg_rad_bearing` decimal(15,4) DEFAULT '-9999.0000',
  `rad_type` int DEFAULT '-9999',
  `spectra_type` int DEFAULT '-9999',
  PRIMARY KEY (`site_id`,`network_id`,`time`,`patterntype`),
  KEY `fk_radialdiag_site1_idx` (`site_id`,`network_id`),
  CONSTRAINT `fk_radialdiag_site1` FOREIGN KEY (`site_id`, `network_id`) REFERENCES `site` (`site_id`, `network_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`rt`@`hfrnet-cs.ucsd.edu`*/ /*!50003 TRIGGER `radialdiag_AINS` AFTER INSERT ON `radialdiag` FOR EACH ROW begin
IF ((select time from latest_radialdiag where site_id = NEW.site_id and network_id = NEW.network_id AND patterntype = NEW.patterntype) < NEW.time) OR isnull((select time from latest_radialdiag where site_id = NEW.site_id and network_id = NEW.network_id AND patterntype = NEW.patterntype)) then
  INSERT INTO latest_radialdiag VALUES (NEW.network_id,NEW.site_id,NEW.time,NEW.patterntype)
    ON DUPLICATE KEY UPDATE time=NEW.time;
end if;
end */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `radialfiles`
--

DROP TABLE IF EXISTS `radialfiles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `radialfiles` (
  `site_id` mediumint unsigned NOT NULL,
  `network_id` mediumint unsigned NOT NULL,
  `time` decimal(17,5) NOT NULL,
  `format` enum('hfrss10lluv','hfrweralluv1.0','ruv') NOT NULL DEFAULT 'hfrss10lluv',
  `patterntype` enum('i','m') NOT NULL DEFAULT 'm',
  `lat` decimal(12,6) DEFAULT NULL,
  `lon` decimal(12,6) DEFAULT NULL,
  `cfreq` decimal(15,11) DEFAULT '-9999.99999999900',
  `range_res` decimal(8,4) DEFAULT '-9999.0000',
  `ref_bearing` decimal(8,4) DEFAULT '-9999.0000',
  `nrads` int DEFAULT NULL,
  `dres` decimal(12,8) DEFAULT '-9999.00000000',
  `manufacturer` char(50) DEFAULT '-',
  `xmit_sweep_rate` decimal(12,8) DEFAULT '-9999.00000000',
  `xmit_bandwidth` decimal(15,8) DEFAULT '-9999.00000000',
  `max_curr_lim` decimal(15,8) DEFAULT '-9999.00000000',
  `min_rad_vect_pts` int DEFAULT '-1',
  `loop1_amp_corr` decimal(12,2) DEFAULT '-9999.00',
  `loop2_amp_corr` decimal(12,2) DEFAULT '-9999.00',
  `loop1_phase_corr` decimal(10,2) DEFAULT '-9999.00',
  `loop2_phase_corr` decimal(10,2) DEFAULT '-9999.00',
  `bragg_smooth_pts` int DEFAULT '-1',
  `rad_bragg_peak_dropoff` decimal(10,2) DEFAULT '-9999.00',
  `second_order_bragg` int DEFAULT '-1',
  `rad_bragg_peak_null` decimal(12,2) DEFAULT '-9999.00',
  `rad_bragg_noise_thr` decimal(12,2) DEFAULT '-9999.00',
  `music_param_01` decimal(12,2) DEFAULT '-9999.00',
  `music_param_02` decimal(12,2) DEFAULT '-9999.00',
  `music_param_03` decimal(12,2) DEFAULT '-9999.00',
  `ellip` char(50) DEFAULT '-',
  `earth_radius` decimal(21,15) DEFAULT '-9999.000000000000000',
  `ellip_flatten` decimal(24,9) DEFAULT '-9999.000000000',
  `rad_merger_ver` char(16) DEFAULT '-',
  `spec2rad_ver` char(16) DEFAULT '-',
  `ctf_ver` char(16) DEFAULT '-',
  `lluvspec_ver` char(16) DEFAULT '-',
  `geod_ver` char(25) DEFAULT '-',
  `rad_slider_ver` char(16) DEFAULT '-',
  `rad_archiver_ver` char(16) DEFAULT '-',
  `patt_date` decimal(17,5) DEFAULT '-9999999999.99900',
  `patt_res` decimal(9,2) DEFAULT '-9999.00',
  `patt_smooth` decimal(9,2) DEFAULT '-9999.00',
  `spec_range_cells` int DEFAULT '-1',
  `spec_doppler_cells` int DEFAULT '-1',
  `curr_ver` char(16) DEFAULT '-',
  `codartools_ver` char(16) DEFAULT '-',
  `first_order_calc` int DEFAULT '-1',
  `lluv_tblsubtype` char(20) DEFAULT '-',
  `proc_by` char(50) DEFAULT '-',
  `merge_method` int DEFAULT '-1',
  `patt_method` int DEFAULT '-1',
  `dir` char(128) DEFAULT NULL,
  `dfile` char(64) DEFAULT NULL,
  `mtime` decimal(17,5) DEFAULT NULL,
  `sampling_period_hrs` decimal(8,4) DEFAULT NULL,
  `nmerge_rads` int DEFAULT NULL,
  `proc_time` decimal(17,5) DEFAULT NULL,
  `range_bin_start` int DEFAULT NULL,
  `range_bin_end` int DEFAULT NULL,
  `loop1_amp_calc` decimal(15,2) DEFAULT NULL,
  `loop2_amp_calc` decimal(15,2) DEFAULT NULL,
  `loop1_phase_calc` decimal(15,2) DEFAULT NULL,
  `loop2_phase_calc` decimal(15,2) DEFAULT NULL,
  `file_arrival_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`site_id`,`network_id`,`time`,`format`,`patterntype`),
  KEY `fk_radialmeta_site1_idx` (`site_id`,`network_id`),
  CONSTRAINT `fk_radialmeta_site1` FOREIGN KEY (`site_id`, `network_id`) REFERENCES `site` (`site_id`, `network_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`rt`@`hfrnet-cs.ucsd.edu`*/ /*!50003 TRIGGER `radialfiles_AINS` AFTER INSERT ON `radialfiles` FOR EACH ROW begin
IF ((select time from latest_radialfiles where site_id = NEW.site_id and network_id = NEW.network_id AND patterntype = NEW.patterntype) < NEW.time) OR isnull((select time from latest_radialfiles where site_id = NEW.site_id and network_id = NEW.network_id AND patterntype = NEW.patterntype)) then
  INSERT INTO latest_radialfiles VALUES (NEW.network_id,NEW.site_id,NEW.time,NEW.patterntype)
    ON DUPLICATE KEY UPDATE time=NEW.time;
end if;
end */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`rt`@`hfrnet-cs.ucsd.edu`*/ /*!50003 TRIGGER `radialfiles_AD` AFTER DELETE ON `radialfiles` FOR EACH ROW begin
DELETE FROM hardwarediag WHERE site_id=OLD.site_id AND network_id=OLD.network_id AND time=OLD.time;
DELETE FROM radialdiag WHERE site_id=OLD.site_id AND network_id=OLD.network_id AND time=OLD.time AND patterntype=OLD.patterntype;
end */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `site`
--

DROP TABLE IF EXISTS `site`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `site` (
  `site_id` mediumint unsigned NOT NULL AUTO_INCREMENT,
  `network_id` mediumint unsigned NOT NULL,
  `sta` char(10) NOT NULL,
  `staname` char(50) DEFAULT '-',
  `decommissioned` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`sta`,`site_id`,`network_id`),
  UNIQUE KEY `site_id_UNIQUE` (`site_id`,`network_id`),
  KEY `fk_site_network_idx` (`network_id`),
  CONSTRAINT `fk_site_network` FOREIGN KEY (`network_id`) REFERENCES `network` (`network_id`)
) ENGINE=InnoDB AUTO_INCREMENT=345 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `siteNotifications`
--

DROP TABLE IF EXISTS `siteNotifications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `siteNotifications` (
  `id` int NOT NULL AUTO_INCREMENT,
  `timestamp` datetime DEFAULT NULL,
  `site` varchar(5) DEFAULT NULL,
  `message` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=307907 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `wavefiles`
--

DROP TABLE IF EXISTS `wavefiles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `wavefiles` (
  `site_id` mediumint unsigned NOT NULL,
  `network_id` mediumint unsigned NOT NULL,
  `time` decimal(17,5) NOT NULL,
  `CTF` char(10) DEFAULT '-',
  `FileType` varchar(25) DEFAULT '-',
  `UUID` varchar(50) DEFAULT '-',
  `Manufacturer` char(50) DEFAULT '-',
  `TimeMarks` char(10) DEFAULT '-',
  `TimeZone` char(20) DEFAULT '-',
  `lat` decimal(12,6) DEFAULT NULL,
  `lon` decimal(12,6) DEFAULT NULL,
  `TimeCoverage` char(20) DEFAULT '-',
  `RangeResolutionKMeters` decimal(8,4) DEFAULT '-9999.0000',
  `AntennaBearing` decimal(4,1) DEFAULT '-999.0',
  `RangeCells` int DEFAULT NULL,
  `DopplerCells` int DEFAULT NULL,
  `TransmitCenterFreqMHz` decimal(12,8) DEFAULT '-9999.00000000',
  `TransmitBandwidthKHz` decimal(12,8) DEFAULT '-9999.00000000',
  `TransmitSweepRateHz` decimal(12,8) DEFAULT '-9999.00000000',
  `CoastlineSector` varchar(12) DEFAULT '-',
  `CurrentVelocityLimit` int DEFAULT NULL,
  `BraggSmoothingPoints` int DEFAULT NULL,
  `BraggHasSecondOrder` int DEFAULT NULL,
  `WaveBraggNoiseThreshold` float DEFAULT NULL,
  `WaveBraggPeakDropOff` float DEFAULT NULL,
  `WaveBraggPeakNull` float DEFAULT NULL,
  `MaximumWavePeriod` float DEFAULT NULL,
  `WaveBearingLimits` varchar(12) DEFAULT '-',
  `WaveUseInnerBragg` bit(1) DEFAULT b'0',
  `WaveSecondOrderMethod` int DEFAULT NULL,
  `WavesFollowTheWind` bit(1) DEFAULT b'0',
  `WaveSaturationRatio` float DEFAULT NULL,
  `WaveHeightLimit` float DEFAULT NULL,
  `WavePeriodSetLimit` float DEFAULT NULL,
  `PatternUUID` varchar(50) DEFAULT '-',
  `WaveMergeMethod` bit(10) DEFAULT NULL,
  `WaveReductionMethod` bit(10) DEFAULT NULL,
  `WaveMinDopplerPoints` int DEFAULT NULL,
  `WaveMinVectors` int DEFAULT NULL,
  `WaveMaximumWaveHeight` float DEFAULT NULL,
  `WaveMaximumWavePeriodChange` float DEFAULT NULL,
  `WaveOutlierLowerPercentage` float DEFAULT NULL,
  `WaveOutlierUpperPercentage` float DEFAULT NULL,
  `MWHT` float DEFAULT NULL,
  `MWPD` float DEFAULT NULL,
  `WAVB` float DEFAULT NULL,
  `WNDB` float DEFAULT NULL,
  `PMWH` float DEFAULT NULL,
  `ACNT` int DEFAULT NULL,
  `DIST` float DEFAULT NULL,
  `LOND` decimal(12,6) DEFAULT NULL,
  `LATD` decimal(12,6) DEFAULT NULL,
  `RCLL` int DEFAULT NULL,
  `WDPT` int DEFAULT NULL,
  `MTHD` int DEFAULT NULL,
  `FLAG` int DEFAULT NULL,
  `WHNM` int DEFAULT NULL,
  `WHSD` float DEFAULT NULL,
  `ProcessedTimeStamp` decimal(17,5) DEFAULT NULL,
  `WaveModelFilter` char(16) DEFAULT '-',
  `SpectraToWavesModel` char(16) DEFAULT '-',
  `WaveModelForFive` char(16) DEFAULT '-',
  `WaveModelArchiver` char(16) DEFAULT '-',
  `AnalyzeSpectra` char(16) DEFAULT '-',
  PRIMARY KEY (`site_id`,`network_id`,`time`),
  KEY `fk_wavefile_site1_idx` (`site_id`,`network_id`),
  CONSTRAINT `fk_wavefile_site1` FOREIGN KEY (`site_id`, `network_id`) REFERENCES `site` (`site_id`, `network_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-04-03 21:46:13
