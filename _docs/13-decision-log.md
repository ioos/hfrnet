---
# Feel free to add content and custom Front Matter to this file.
# To modify the layout, see https://jekyllrb.com/docs/themes/#overriding-theme-defaults

title: Decision Log
layout: home
---

# 13. Decision Log

The final thing you might consider including in a software guidebook is a log of the decisions that have been made during the development of the software system.

## Intent

The purpose of this section is to simply record the major decisions that have been made, including both the technology choices (e.g. products, frameworks, etc) and the overall architecture (e.g. the structure of the software, architectural style, decomposition, patterns, etc). For example:

- Why did you choose technology or framework “X” over “Y” and “Z”?
- How did you do this? Product evaluation or proof of concept?
- Were you forced into making a decision about “X” based upon corporate policy or
enterprise architecture strategies?
- Why did you choose the selected software architecture? What other options did you
consider?
- How do you know that the solution satisfies the major non-functional requirements?
- etc

## Structure

Again, keep it simple, with a short paragraph or architecture decision record describing each decision that you want to record. Do refer to other resources such as proof of concepts, performance testing results or product evaluations if you have them.

## Motivation

The motivation for recording the significant decisions is that this section can act as a point of reference in the future. All decisions are made given a specific context and usually have trade-offs. There is usually never a perfect solution to a given problem. Articulating the decision making process after the event is often complex, particularly if you’re explaining the decision to people who are joining the team or you’re in an environment where the context changes on a regular basis.
Although “nobody ever gets fired for buying IBM”, perhaps writing down the fact that corporate policy forced you into using IBM WebSphere over Apache Tomcat will save you some tricky conversations in the future.

## Audience

The audience for this section is predominantly the technical people in the software develop- ment team along with others that may help deploy, support and operate the software system.

## Required

No, but I usually include this section if we (the team) spend more than a few minutes thinking about something significant such as a technology choice or an architectural style. If in doubt, spend a couple of minutes writing it down, especially if you work for a consulting organisation who is building a software system under an outsourcing agreement for a customer.
