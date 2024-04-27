---
title: HFRNet Users
layout: page
---

For each user below, document their needs by answering the following questions:

1. Where do you currently access data?
2. Who is the main POC?
3. What are your spatiotemporal requirements (geographic domain, data latency, temporal window)

- HFR Station
- Web Visualization (External web sites that rely on a service currently provided by SIO or NDBC (e.g. ncWMS or the SIO map server) to visualize HFR data on their web platform)
- NCEP Data tanks (Decoder team pulls data from the NDBC THREDDS server to create files in the NCEP data tanks.)
- USCG SAROPS (How does RPS gather data to provide to USCG?)
- RPS EDS (This may be the same as the SAROPS use case above.)
- Oceansmap (How do these files get to RPS?  We shouldn't assume that it is the same path as EDS/SAROPS)
- RTOFS (This customer is still To Be Developed, but their requirement for global data should be part of our panning.)
- WCOFS (This is probably covered by the Data Tanks use case.)
- STPS (How do they retrieve input data?)
- ROMS Radial DA (Presumably they pull from teh Radials ERDDAP.  Confirm, then investigate strengths/weaknesses and extensions to other external radial data assimilation efforts.)
- Radials ERDDAP (Confirm exactly how they retrieve data)
- RTV THREDDS (Document known users of the SIO vs NDBC THREDDS.  We need to understand the reasons users depart one server for another.  Reliability, data latency, availability of aggregations? Other?)
- ARCO Cloud Data Lake (Future goal to provide aggregated, cloud optimized research quality access to RTV and Radials.)
- NWS Telecom Gateway (Confirm POCs and data flow.  Do we need to involve Decoder team?  NOS POC Wei Wu?)
- AWIPS (Document POC.  Which data is currently flowing to the AWIPS terminals and how?  What is NDBC role?)
- CO-OPS PORTS (Confirm data flow and reliability requirements.  POC is Chris Deveglio or his delegate.)
- GNOME/GOODS (How does ORR access?  POC is probably Chris Barker or Amy MacFayden)
- Doppio model run by Rutgers/MARACOOS ([A data-assimilative model reanalysis of the U.S. Mid Atlantic Bight and Gulf of Maine: Configuration and comparison to observations and global ocean models](https://www.sciencedirect.com/science/article/pii/S0079661122001781))


USCG EDS and Search-and-Rescue Optimal Planning System (SAROPS)
USCG SAROPS (How does RPS gather data to provide to USCG?)
Current Access Location (URL/format): 
Primary POC (name/email):
Spatio-temporal requirements (including data latency):
USCG Environmental Data Server (EDS), operated by Tetratech/RPS Group: 
Current Access Location (URL/format): 
Primary POC (name/email):
Spatio-temporal requirements (including data latency):

NCEP Data Tanks 
The NCEP HPC Dataflow team maintains the scripts that pull data from the NDBC THREDDS server to create files in the NCEP data tanks.  The basic functionality of the script is to poll the NDBC THREDDS server hourly, and then WGET changed files onto the data tank filesystem.  The HPC Dataflow team specializes in WCOSS, dcom, and decoders. 
Current Access Location (URL/format): https://dods.ndbc.noaa.gov/thredds/catalog/hfradar/catalog.html, files saved to data tank directory: /lfs/h1/ops/prod/dcom/20240402/wgrdbul/ndbc. 
Primary POC (name/email): nco.hpc.dataflow@noaa.gov 
Spatio-temporal requirements (including data latency):

Real-Time Ocean Forecast System
RTOFS (This customer is still To Be Developed, but their requirement for global data should be part of our planning.)
Current Access Location (URL/format): 
Primary POC (name/email): Avichal Mehra
Spatio-temporal requirements (including data latency):
West Coast Operational Forecast System
WCOFS (Currently using RTV netCDF files; roadmap includes migrating to radials at some point.)
Current Access Location (URL/format): /lfs/h1/ops/prod/dcom/20240402/wgrdbul/ndbc contains copies of the netCDF field served via the NDBC TDS.
Primary POC (name/email): CO-OPS - Lianyuan Zheng, OCS - Alex Kurapov and Wei Wu
Spatio-temporal requirements (including data latency):

NWS Telecommunications Gateway


Current Access Location (URL/format): NDBC Pushes Grib files containing Realtime vectors from their communications servers to the NWSTG.
Primary POC (name/email): Fang Wang (as of 2024) fang.wang@noaa.gov and IDP Dataflow Team nco.idp.dataflow@noaa.gov.  At NDBC: Kevin Hill - NOAA Federal, POC for sending HFRadar data via Line 421.
Spatio-temporal requirements (including data latency): 

Advanced Weather Interactive Processing System
Advanced Weather Interactive Processing System (AWIPS) (Document POC.  Which data currently flows to the AWIPS terminals and how?  What is NDBC's role?)
Current Access Location (URL/format): 
Primary POC (name/email):
Spatio-temporal requirements (including data latency):

Operational Radials User TBD
Radials user? (NOTE: Figure 7 suggests that the NDBC Communications server pushes radials to the NWSTG, possibly in ASCII formats.  Can we verify this customer below, please?))
Current Access Location (URL/format): 
Primary POC (name/email):
Spatio-temporal requirements (including data latency):

SIO THREDDS Server
Short-Term Prediction System (STPS) model

STPS (How do they retrieve  input data?)
Current Access Location (URL/format): 
Primary POC (name/email):
Spatio-temporal requirements (including data latency):

General NOAA Operational Modeling Environment (GNOME) Online Oceanographic Data Server (GOODS)
GNOME/GOODS (How does ORR access?  POC is probably Chris Barker or Amy MacFayden)
Current Access Location (URL/format): 
Primary POC (name/email):
Spatio-temporal requirements (including data latency):
Oceansmap Web Visualization System
Oceansmap (How do these files get to RPS?  We shouldn't assume that it is the same path as EDS/SAROPS)
Current Access Location (URL/format): RPS pulls from the SIO THREDDS
Primary POC (name/email):
Spatio-temporal requirements (including data latency):


National Centers for Environmental Information (NCEI)
NDBC and NCEI work together to create a monthly archive package.  How is it working?  Are there tweaks we need to make?  How does it factor into our plans with NCEI, GCOD etc?.)
Current Access Location (URL/format): 
Primary POC (name/email):
Spatio-temporal requirements (including data latency):



Radials ERDDAP (or non-NOAA operational modeling clients)
Current Access Location (URL/format): Access the SIO/CORDC FTP server on the SIO Node.
Primary POC (name/email): Kelly Knee
Spatio-temporal requirements (including data latency):
Doppio Model at MARACOOS
John Wilkin Rutgers/MARACOOS running Doppio
John Wilkin's reply:  “We are not using radials operationally. However, a resource like the radial server is essential to future experimentation….”
Current Access Location (URL/format): 
Primary POC (name/email):
Spatio-temporal requirements (including data latency):
Central California ROMS
Andy Moore/Chris Edwards UCSC/CeNCOOS running California Current model (name?)
Current Access Location (URL/format): 
Primary POC (name/email):
Spatio-temporal requirements (including data latency):
Central Pac ROMS at PacIOOS
Brian Powell UH/PacIOOS running a regional South Pacific ROMS model
Reply from Brian Powell:  “We have been using HFR radials in real-time operational mode [for our Hawaiian Islands ROMS model] since 2010; however, we do not pull them from the… [IOOS Radials ERDDAP] server. We pull it straight from the raw input generated by… [Pierre Flament’s LERA] HFR sites [only that are on the Hawaiian Islands].”
Current Access Location (URL/format): 
Primary POC (name/email):
Spatio-temporal requirements (including data latency):
Other Radials ERDDAP Customers
Reply from Kelly Knee:  “We reviewed the last 10 days [prior to 4/11/2024] of the NGINX logs [for the IOOS Radials ERDDAP Server].  In that time 20 unique IP addresses visited the site and made 437 requests for data.  Egress volumes are less than 100GB per month, which is not surprising given the nature of the files.”

External Web Visualizations
Web Visualization (External websites that rely on a service currently provided by SIO or NDBC (e.g., ncWMS or the SIO map server) to visualize HFR data on their web platform)
Current Access Location (URL/format): 
Primary POC (name/email):
Spatio-temporal requirements (including data latency):
This is an important topic to investigate, perhaps at the DMAC meeting.  A dedicated standards based GIS visualization server is not something we've developed or prioritized.  But, over the years there have been groups that used ncWMS on THREDDS with some success, but it's been problematic (ask Jim P.).  Also, SIO created a visualization service that (I think) was not a true WMS server but did serve some sort of images.  People liked it and used it but it was not reliable.  I'd like to incorporate this requirement into our planning, though possibly for a second or third phase.  This needs to provide visualization services is a general DMAC need.
From recent DMAC Annual meeting, Jim Potemra confirmed that PacIOOS is a ncWMS user.  They would prefer accessing an NCWMS on NDBC THREDDS but currently access SIO THREDDS.



Center for Operational Oceanographic Products & Services (CO-OPS) Physical Oceanographic Real-Time System (PORTS)
POC: Chris Paternostro or Chris Deveglio:
Current response: “We don't pull data right now. We create predictions of the data pulled once in a while, like 5+ years ago [from the SIO THREDDS].” CO-OPS plans to 1) pull all HFR data every five years to create HA currents predictions at all HFR footprints (right now they have done this only once), and 2) add it as a layer on the OceansMap interface via TetraTech.  (When is the next pull?) Years from now.  -- Chris Paternostro, CO-OPS
 
Cloud-Hosted Analysis Environment
This currently does not exist and should probably be moved from this document to a plan.  

ARCO Cloud Data Lake (Future goal to provide aggregated, cloud-optimized research quality access to RTV and Radials.)
Current Access Location (URL/format): 
Primary POC (name/email):
Spatio-temporal requirements (including data latency):

