---
# Feel free to add content and custom Front Matter to this file.
# To modify the layout, see https://jekyllrb.com/docs/themes/#overriding-theme-defaults

title: Principles
layout: home
---

## 5. Principles

Principles
The principles section allows you to summarise those principles that have been used (or you are using) to design and build the software.

## Intent

The purpose of this section is to simply make it explicit which principles you are following. These could have been explicitly asked for by a stakeholder or they could be principles that you (i.e. the software development team) want to adopt and follow.

## Structure

If you have an existing set of software development principles (e.g. on a development wiki), by all means simply reference it. Otherwise, list out the principles that you are following and accompany each with a short explanation or link to further information. Example principles include:

- Architectural layering strategy.
- No business logic in views.
- No database access in views.
- Use of interfaces.
- Always use an ORM.
- Dependency injection.
- The Hollywood principle (don’t call us, we’ll call you).
- High cohesion, low coupling.
- Follow SOLID (Single responsibility principle, Open/closed principle, Liskov substitu-
tion principle, Interface segregation principle, Dependency inversion principle).
- DRY (don’t repeat yourself).
- Ensure all components are stateless (e.g. to ease scaling).
- Prefer a rich domain model.
- Prefer an anaemic domain model.
- Always prefer stored procedures.
- Never use stored procedures.
- Don’t reinvent the wheel.
- Common approaches for error handling, logging, etc. -  Buy rather than build.
- etc

## Motivation

The motivation for writing down the list of principles is to make them explicit so that everybody involved with the software development understands what they are. Why? Put simply, principles help to introduce consistency into a codebase by ensuring that common problems are approached in the same way.

## Audience

The audience for this section is predominantly the technical people in the software develop- ment team.

## Required

Yes, all software guidebooks should include a summary of the principles that have been or are being used to develop the software.


- Multi-stage migration
- Change the fewest number of system components as possible during each stage of the migration.
- Open source code for all portal and node functions (Create ioos/hfrnet github repository to serve as the master repo for planning and version control.  OK to create new repos to facilitate a modular and open architecture.  e.g. separate "science code" from "synchronizing and monitoring data flow")
