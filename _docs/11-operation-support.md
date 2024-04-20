---
# Feel free to add content and custom Front Matter to this file.
# To modify the layout, see https://jekyllrb.com/docs/themes/#overriding-theme-defaults

title: Operation and Support
layout: home
---

The operations and support section allows you to describe how people will run, monitor and manage your software.

## Intent

Most systems will be subject to support and operational requirements, particularly around how they are monitored, managed and administered. Including a dedicated section in the software guidebook lets you be explicit about how your software will or does support those requirements. This section should address the following types of questions:

- Isitclearhowthesoftwareprovidestheabilityforoperation/supportteamstomonitor and manage the system?
- How is this achieved across all tiers of the architecture?
- How can operational staff diagnose problems?
- Where are errors and information logged? (e.g. log files, Windows Event Log, SMNP,
JMX, WMI, custom diagnostics, etc)
- Do configuration changes require a restart?
- Arethereanymanualhousekeepingtasksthatneedtobeperformedonaregularbasis?
- Does old data need to be periodically archived?

## Structure

This section is usually fairly narrative in nature, with a heading for each related set of information (e.g. monitoring, diagnostics, configuration, etc).

## Motivation

I’ve undertaken audits of existing software systems in the past and we’ve had to spend time hunting for basic information such as log file locations. Times change and team members move on, so recording this information can help prevent those situations in the future where nobody understands how to operate the software.

## Audience

The audience for this section is predominantly the technical people in the software develop- ment team along with others that may help deploy, support and operate the software system.

## Required

Yes, an operations and support section should be included in all software guidebooks, unless you like throwing software into a black hole and hoping for the best!


There is a role that was filled by Joe Chen and/or Mark Otero to provide some level of operator support.  

- What are the essential functions they provided and are they adequately captured in the new system?  
- Does this support role move to the IOOS Office?  If so, where specifically?  
- How much of this support function can be addressed by a new management or dashboard web site?  
