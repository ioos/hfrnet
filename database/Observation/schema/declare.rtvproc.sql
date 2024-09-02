-- MySQL dump 10.13  Distrib 8.0.33, for Linux (x86_64)
--
-- Host: localhost    Database: rtvproc
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
-- Table structure for table `combine_method`
--

DROP TABLE IF EXISTS `combine_method`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `combine_method` (
  `id` tinyint unsigned NOT NULL AUTO_INCREMENT,
  `name` enum('uwls') NOT NULL COMMENT 'Method abbreviation, e.g. uwls, oi, etc.',
  `description` varchar(45) NOT NULL COMMENT 'Descriptive method name',
  PRIMARY KEY (`id`),
  UNIQUE KEY `method_idx` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb3 COMMENT='RTV combine method definitions';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `domain`
--

DROP TABLE IF EXISTS `domain`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `domain` (
  `id` tinyint unsigned NOT NULL AUTO_INCREMENT,
  `name` enum('uswc','usegc','ushi','prvi','gak','akns','glna') NOT NULL COMMENT 'Abbreviated domain identifier',
  `description` varchar(45) NOT NULL COMMENT 'Domain description',
  PRIMARY KEY (`id`),
  UNIQUE KEY `domain_idx` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb3 COMMENT='RTV processing domains';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `lta_parameter`
--

DROP TABLE IF EXISTS `lta_parameter`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `lta_parameter` (
  `id` tinyint unsigned NOT NULL AUTO_INCREMENT,
  `domain_id` tinyint unsigned NOT NULL,
  `resolution_id` tinyint unsigned NOT NULL,
  `combine_method_id` tinyint unsigned NOT NULL,
  `min_month_temporal_coverage` tinyint unsigned NOT NULL DEFAULT '21' COMMENT 'Minimum temporal coverage in a month required to produce an average for a given grid point (days)',
  `min_year_temporal_coverage` smallint unsigned NOT NULL DEFAULT '274' COMMENT 'Minimum temporal coverage in a year required to produce an average for a given grid point (days)',
  `max_error` float unsigned NOT NULL DEFAULT '1.25' COMMENT 'Maximum error allowed in contributing to average (HDOP for UWLS, normalized uncertinty for OI)',
  PRIMARY KEY (`id`),
  UNIQUE KEY `ltam_uq_idx` (`domain_id`,`resolution_id`,`combine_method_id`),
  KEY `ltam_res_fk_idx` (`domain_id`),
  KEY `ltam_res_fk_idx1` (`resolution_id`),
  KEY `ltam_method_fk_idx` (`combine_method_id`),
  CONSTRAINT `ltam_dom_fk` FOREIGN KEY (`domain_id`) REFERENCES `domain` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `ltam_method_fk` FOREIGN KEY (`combine_method_id`) REFERENCES `combine_method` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `ltam_res_fk` FOREIGN KEY (`resolution_id`) REFERENCES `resolution` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb3 COMMENT='Long Term Average (LTA) parameters';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `process`
--

DROP TABLE IF EXISTS `process`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `process` (
  `id` tinyint unsigned NOT NULL AUTO_INCREMENT,
  `combine_method_id` tinyint unsigned NOT NULL,
  `name` enum('RTV','STC','LTA') NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `process_uq` (`combine_method_id`,`name`),
  KEY `process_method_fk_idx` (`combine_method_id`),
  CONSTRAINT `process_method_fk` FOREIGN KEY (`combine_method_id`) REFERENCES `combine_method` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb3 COMMENT='Associates processing with domains and resolutions';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `realtime_process`
--

DROP TABLE IF EXISTS `realtime_process`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `realtime_process` (
  `id` tinyint unsigned NOT NULL AUTO_INCREMENT,
  `domain_id` tinyint unsigned NOT NULL,
  `resolution_id` tinyint unsigned NOT NULL,
  `process_id` tinyint unsigned NOT NULL,
  `priority` tinyint unsigned NOT NULL,
  `status` enum('disabled','enabled') NOT NULL DEFAULT 'enabled',
  `save_as` set('ascii','netcdf') NOT NULL DEFAULT '',
  PRIMARY KEY (`id`),
  UNIQUE KEY `rtproc_uqproc_idx` (`domain_id`,`resolution_id`,`process_id`),
  UNIQUE KEY `rtproc_uqpri_idx` (`domain_id`,`resolution_id`,`priority`),
  KEY `rtproc_dom_fk_idx` (`domain_id`),
  KEY `rtproc_res_fk_idx` (`resolution_id`),
  KEY `rtproc_process_fk_idx` (`process_id`),
  CONSTRAINT `rtproc_dom_fk` FOREIGN KEY (`domain_id`) REFERENCES `domain` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `rtproc_process_fk` FOREIGN KEY (`process_id`) REFERENCES `process` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `rtproc_res_fk` FOREIGN KEY (`resolution_id`) REFERENCES `resolution` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=61 DEFAULT CHARSET=utf8mb3 COMMENT='Defines near real-time processing';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `resolution`
--

DROP TABLE IF EXISTS `resolution`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `resolution` (
  `id` tinyint unsigned NOT NULL AUTO_INCREMENT,
  `name` enum('500m','1km','2km','6km') NOT NULL COMMENT 'Abbreviated resolution identifier',
  PRIMARY KEY (`id`),
  UNIQUE KEY `resolution_idx` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb3 COMMENT='RTV processing resolutions';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `rtv_parameter`
--

DROP TABLE IF EXISTS `rtv_parameter`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rtv_parameter` (
  `id` tinyint unsigned NOT NULL AUTO_INCREMENT,
  `domain_id` tinyint unsigned NOT NULL,
  `resolution_id` tinyint unsigned NOT NULL,
  `combine_method_id` tinyint unsigned NOT NULL,
  `max_age` tinyint unsigned NOT NULL DEFAULT '25' COMMENT 'Maximum data age that will be (re)processed (hours)',
  `min_rad_sites` tinyint unsigned NOT NULL DEFAULT '2' COMMENT 'Minimum number of radial sites required to make a total solution',
  `min_radials` tinyint unsigned NOT NULL DEFAULT '3' COMMENT 'Minimum number of radials required to make a solution',
  `max_rad_speed` smallint unsigned NOT NULL DEFAULT '100' COMMENT 'Maximum radial speed allowed to contribute to RTV solutions (cm/s)',
  `grid_search_radius` float unsigned NOT NULL COMMENT 'Search radius used for finding radial solutions (km)',
  `max_rtv_speed` smallint unsigned NOT NULL DEFAULT '100' COMMENT 'Maximum RTV speed allowed (cm/s)',
  `uwls_max_hdop` float unsigned DEFAULT '10' COMMENT 'Maximum GDOP threshold for mat files',
  `uwls_max_hdop_ascii` float unsigned DEFAULT '1.25' COMMENT 'Maximum GDOP threshold for ascii files',
  `uwls_max_hdop_nc` float unsigned DEFAULT '1.25' COMMENT 'Maximum GDOP threshold for NetCDF files',
  PRIMARY KEY (`id`),
  UNIQUE KEY `rtvparam_uq_idx` (`domain_id`,`resolution_id`,`combine_method_id`),
  KEY `rtvparam_dom_fk_idx` (`domain_id`),
  KEY `rtvparam_res_fk_idx` (`resolution_id`),
  KEY `rtvparam_method_fk_idx` (`combine_method_id`),
  CONSTRAINT `rtvparam_dom_fk` FOREIGN KEY (`domain_id`) REFERENCES `domain` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `rtvparam_method_fk` FOREIGN KEY (`combine_method_id`) REFERENCES `combine_method` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `rtvparam_res_fk` FOREIGN KEY (`resolution_id`) REFERENCES `resolution` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb3 COMMENT='RTV processing parameters';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `site`
--

DROP TABLE IF EXISTS `site`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `site` (
  `id` smallint unsigned NOT NULL AUTO_INCREMENT,
  `network` varchar(45) NOT NULL COMMENT 'Network abbreviation',
  `name` varchar(45) NOT NULL COMMENT 'site name abbreviation',
  PRIMARY KEY (`id`),
  UNIQUE KEY `site_idx` (`network`,`name`)
) ENGINE=InnoDB AUTO_INCREMENT=298 DEFAULT CHARSET=utf8mb3 COMMENT='Site definitions for RTV processing';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `site_config`
--

DROP TABLE IF EXISTS `site_config`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `site_config` (
  `id` smallint unsigned NOT NULL AUTO_INCREMENT,
  `site_id` smallint unsigned NOT NULL,
  `domain_id` tinyint unsigned NOT NULL,
  `resolution_id` tinyint unsigned NOT NULL,
  `start_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Processing dates and times greater than or equal to this value AND\nless than the end_time should use this configuration.',
  `end_time` timestamp NULL DEFAULT NULL COMMENT 'Processing dates and times less than this value AND greater than\nor equal to the start_time should use this configuration.',
  `beampattern` enum('ideal','measured') NOT NULL COMMENT 'Beam pattern for RTV processing',
  `use_radial_minute` tinyint unsigned NOT NULL DEFAULT '0' COMMENT 'Radial data timestamp minute to use in RTV processing. Some sites\nreport multiple times per hour or otherwise don''t report at the top of \nthe hour.  This value defines the minute of the radial data timestamp\nto be used.',
  PRIMARY KEY (`id`),
  KEY `siteconfig_res_fk_idx` (`resolution_id`),
  KEY `siteconfig_site_fk_idx` (`site_id`),
  KEY `siteconfig_dom_fk_idx` (`domain_id`),
  CONSTRAINT `siteconfig_dom_fk` FOREIGN KEY (`domain_id`) REFERENCES `domain` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `siteconfig_res_fk` FOREIGN KEY (`resolution_id`) REFERENCES `resolution` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `siteconfig_site_fk` FOREIGN KEY (`site_id`) REFERENCES `site` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=31247 DEFAULT CHARSET=utf8mb3 COMMENT='Time-dependent site configurations for RTV processing';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `state`
--

DROP TABLE IF EXISTS `state`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `state` (
  `id` tinyint unsigned NOT NULL AUTO_INCREMENT,
  `domain_id` tinyint unsigned NOT NULL,
  `resolution_id` tinyint unsigned NOT NULL,
  `name` varchar(45) NOT NULL,
  `time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `csv` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `state_idx` (`domain_id`,`resolution_id`,`name`),
  KEY `state_dom_fk_idx` (`domain_id`),
  KEY `state_res_fk_idx` (`resolution_id`),
  CONSTRAINT `state_dom_fk` FOREIGN KEY (`domain_id`) REFERENCES `domain` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `state_res_fk` FOREIGN KEY (`resolution_id`) REFERENCES `resolution` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=82 DEFAULT CHARSET=utf8mb3 COMMENT='State tracking';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `stc_parameter`
--

DROP TABLE IF EXISTS `stc_parameter`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `stc_parameter` (
  `id` tinyint unsigned NOT NULL AUTO_INCREMENT,
  `domain_id` tinyint unsigned NOT NULL,
  `resolution_id` tinyint unsigned NOT NULL,
  `combine_method_id` tinyint unsigned NOT NULL,
  `min_temporal_coverage` tinyint unsigned NOT NULL DEFAULT '18' COMMENT 'Minimum temporal coverage required to produce an average for a given grid point (hours)',
  `max_age` tinyint unsigned NOT NULL DEFAULT '50' COMMENT 'Maximum data age that will be (re)processed (hours)',
  `max_error` float unsigned NOT NULL DEFAULT '1.25' COMMENT 'Maximum error allowed in contributing to average (HDOP for UWLS, normalized uncertinty for OI)',
  PRIMARY KEY (`id`),
  UNIQUE KEY `stc_uq_idx` (`domain_id`,`resolution_id`,`combine_method_id`),
  KEY `stc_dom_fk_idx` (`domain_id`),
  KEY `stc_res_fk_idx` (`resolution_id`),
  KEY `stc_method_fk_idx` (`combine_method_id`),
  CONSTRAINT `stc_dom_fk` FOREIGN KEY (`domain_id`) REFERENCES `domain` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `stc_method_fk` FOREIGN KEY (`combine_method_id`) REFERENCES `combine_method` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `stc_res_fk` FOREIGN KEY (`resolution_id`) REFERENCES `resolution` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb3 COMMENT='Sub-tidal current product processing definitions';
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-04-03 21:45:37
