---
title: HFRNet Users
layout: home
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