# 1. Use existing aggregation portals

Date: 2024-04-16

## Status

Accepted

## Context

In the current configuration of HFRNet there are 6-7 aggregation "portals" run by university partners pro bono.  

## Decision

In the first phase (1-2 years) of the HFRNet transition, we will retain the portals and ask university partners to continue operations.  We will seek to decrease the number of portals to 3.  The goal is to minimize the changes needed for the overall system and eliminate the need to change the behavior of the operators of the ca. 165 individual sites.  

## Consequences

The portals are not well funded and constitute a risk to the overall system.  They run software to aggregate radials that may not be consistent with the future design and will need to be considered for future phases.

Portal procedures add latency to the radial aggregations that sometimes introduce spurious features into the calculated surface currents.  This will need to be investigated in a future version.

TODO: consider upgrades to the portal aggregation structure to minimize latency in phase 2 or 3.
