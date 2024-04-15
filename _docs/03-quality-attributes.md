---
# Feel free to add content and custom Front Matter to this file.
# To modify the layout, see https://jekyllrb.com/docs/themes/#overriding-theme-defaults

title: Quality Attributes
layout: home
---

## 3. Quality Attributes

With the functional overview section summarising the functionality, it’s also worth includ- ing a separate section to summarise the quality attributes/non-functional requirements.
Intent
This section is about summarising the key quality attributes and should answer the following types of questions:

- Is there a clear understanding of the quality attributes that the architecture must satisfy?
- Are the quality attributes SMART (specific, measurable, achievable, relevant and timely)?
- Havequalityattributesthatareusuallytakenforgrantedbeenexplicitlymarkedasout of scope if they are not needed? (e.g. “user interface elements will only be presented in English” to indicate that multi-language support is not explicitly catered for)
- Areanyofthequalityattributesunrealistic?(e.g.true24x7availabilityistypicallyvery costly to implement inside many organisations)
In addition, if any of the quality attributes are deemed as “architecturally significant” and therefore influence the architecture, why not make a note of them so that you can refer back to them later in the document.
Structure
Simply listing out each of the quality attributes is a good starting point. Examples include:
- Performance (e.g. latency and throughput)
- Scalability (e.g. data and traffic volumes)
- Availability (e.g. uptime, downtime, scheduled maintenance, 24x7, 99.9%, etc) -  Security (e.g. authentication, authorisation, data confidentiality, etc)
- Extensibility
- Flexibility
- Auditing
- Monitoring and management -  Reliability
- Failover/disaster recovery targets (e.g. manual vs automatic, how long will this take?) -  Business continuity
- Interoperability
- Legal, compliance and regulatory requirements (e.g. data protection act)
- Internationalisation (i18n) and localisation (L10n) -  Accessibility
- Usability
- ...

Each quality attribute should be precise, leaving no interpretation to the reader. Examples where this isn’t the case include:

- “the request must be serviced quickly” -  “there should be no overhead”
- “as fast as possible”
- “as small as possible”
- “as many customers as possible” - ...

## Motivation

If you’ve been a good software architecture citizen and have proactively considered the quality attributes, why not write them down too? Typically, quality attributes are not given to you on a plate and an amount of exploration and refinement is usually needed to come up with a list of them. Put simply, writing down the quality attributes removes any ambiguity both now and during maintenance/enhancement work in the future.

## Audience

Since quality attributes are mostly technical in nature, this section is really targeted at technical people in the software development team.

## Required
Yes, all software guidebooks should include a summary of the quality attributes/non- functional requirements as they usually shape the resulting software architecture in some way.
