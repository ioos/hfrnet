---
# Feel free to add content and custom Front Matter to this file.
# To modify the layout, see https://jekyllrb.com/docs/themes/#overriding-theme-defaults

title: Deployment
layout: home
---
# 10. Deployment

The deployment section is simply the mapping between the software and the infrastructure. 

## Intent

This section is used to describe the mapping between the software (e.g. containers) and the infrastructure. Sometimes this will be a simple one-to-one mapping (e.g. deploy a web application to a single web server) and at other times it will be more complex (e.g. deploy a web application across a number of servers in a server farm). This section answers the following types of questions:

- How and where is the software installed and configured?
- Is it clear how the software will be deployed across the infrastructure elements
described in the infrastructure architecture section? (e.g. one-to-one mapping, multiple
containers per server, etc)
- If this is still to be decided, what are the options and have they been documented?
- Is it understood how memory and CPU will be partitioned between the processes
running on a single piece of infrastructure?
- Areanycontainersand/orcomponentsrunninginanactive-active,active-passive,hot-
standby, cold-standby, etc formation?
- Has the deployment and rollback strategy been defined?
- What happens in the event of a software or infrastructure failure?
- Is it clear how data is replicated across sites?

## Structure

There are a few ways to structure this section:

1. Tables: simple textual tables that show the mapping between software containers and/or components with the infrastructure they will be deployed on.

2. Diagrams:UMLor“boxesandlines”styledeploymentdiagrams,showingthemapping of containers to infrastructure.
In both cases, I may use colour coding the designate the runtime status of software and infrastructure (e.g. active, passive, hot-standby, warm-standby, cold-standby, etc).

## Motivation

The motivation for writing this section is to ensure that I understand how the software is going to work once it gets out of the development environment and also to document the often complex deployment of enterprise software systems.
This section can provide a useful overview, even for those teams that have adopted
continuous delivery and have all of their deployment scripted using tools such as Puppet or Chef.

## Audience

The audience for this section is predominantly the technical people in the software develop- ment team along with others that may help deploy, support and operate the software system.

## Required

Yes, a deployment section should be included in all software guidebooks because it can help to solve the often mysterious question of where the software will be, or has been, deployed.
