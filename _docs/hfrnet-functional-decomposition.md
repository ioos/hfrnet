---
title: HFRNet Functions
layout: home
---


TODO: Need a way of looking at this list of requirements and understanding the current state of our capabiliity.

1. Is the function currently implemented?
2. If yes, where
3. If not, who is the customer and how important is it?
4. If it's important, what part of the new system is most likely to implement it.  When?

Create a requirement allocation matrix with functions going down the rows and System containers/components across the top.  Containers = Portal 1, Portal 2, Portal SIO, Node SIO, Node NDBC, Website, THREDDS SIO, THREDDS NDBC, ERDDAP etc.  Color code existing functions differently from future functions.

Green are mandatory in Phase 1 (prior to 6/30/2025), Yellow could be delayed until Phase 2 (viz. in years 2–3 of operation), and Red could be delayed to Phase 3 (viz. post-Year 3)

# Aggregate Observations

## RangeSeries Aggregator

Aggregate RangeSeries files from all SeaSondes
Aggregate configs and site logs that correspond to each span of RangeSeries
Create archive package

## T.B.D. Aggregator (template for other HFR observations in development)

Aggregate [wind direction; sweep delays; vessel tracks]
Apply Quality Control Algorithms
Create archive package

## Radials Aggregator

Aggregate Radials files from all stations
Aggregate bi-static radials from multi-static stations
Apply Quality Control Algorithms (QARTOD)
Create input to total vector calculation
Create archive package

## Waves Aggregator

Aggregate standard wave files from select wave-capable stations
Aggregate bi-modal wave files from select wave-capable SeaSondes
Aggregate tsunami warnings from select wave-capable stations
Apply Quality Control Algorithms
Create input to tsunami warning system
Create archive package

# Monitor System

## Monitor site health

Monitor site diagnostics
Alert HFR operators of site malfunctions
Automatically suspend data from malfunctioning HFRs

## Monitor network health

Report (tabulate) time of last radial received from each HFR
Monitor 80/80 performance metric
Monitor web site/data server metrics

# Derive Products

## Create CF NetCDF products

Create real-time total vectors
Create aggregated time-series of total vectors
Create real-time wave products
Create aggregated time-series of wave products
Create NetCDFs of radial velocities
Create aggregated time-series of radial velocities
Create NetCDFs of wind directions
Create aggregated time-series of wind directions
Create AI-ready ARCO data products

## Create research products

Create aggregated time-series of sweep delay values
Create aggregated time-series of vessel tracks

## Create operational products

Create GRIB Total Vectors
Create GRIB Waves
Create GRIB Wind Directions
Create BUFR Total Vectors, Waves, and Wind Directions
Create real-time tsunami warning products

# Disseminate Products

## Disseminate to NOAA Systems

Provide data to NWS Telecomm Gateway
Provide data to GTS
Provide data to AWIPS
Provide data to Digital Coast
Provide data to nowCoast

## Disseminate to Public Systems

Provide THREDDS Access
Provide ERDDAP Access
Provide XPublish Access
Provide ARCO Cloud Access

# Visualize Products

## Maintain web portal hfradar.ioos.us

View national map
View site health
Provide technical documentation

## Publish Visualization Services

Publish WMS
Publish Web Tiling Service
Publish Static Images
Publish Geospatial Snapshots (e.g. geoJSON)