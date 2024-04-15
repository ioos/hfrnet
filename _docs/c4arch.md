
# C4 Architecture Template

1. [Context](./01-context)
2. [Functional Overview](./02-functional-overview)
3. [Quality Attributes](03-quality-attributes)
4. [Constraints](04-constraints)
5. [Principles](05-principles)
6. [Software Architecture](06-software-architecture)
7. [Code](07-code)
8. [Data](08-data)
9. [Infrastructure Architecture](09-infrastructure-architecture)
10. [Deployment](10-deployment)
11. [Operation and Support](11-operation-support)
12. [Development Environment](12-development-environment) 
13. [Decision Log](13-decision-log)

## 1. Context

A context section should be one of the first sections of the software guidebook and simply used to set the scene for the remainder of the document.

## Intent

A context section should answer the following types of questions:

- What is this software project/product/system all about?
- What is it that’s being built?
- How does it fit into the existing environment? (e.g. systems, business processes, etc) -  Who is using it? (users, roles, actors, personas, etc)

## Structure

The context section doesn’t need to be long; a page or two is sufficient and a context diagram is a great way to tell most of the story.

## Motivation

I’ve seen software architecture documents that don’t start by setting the scene and, 30 pages in, you’re still none the wiser as to why the software exists and where it fits into the existing IT environment. A context section doesn’t take long to create but can be immensely useful, especially for those outside of the team.

## Audience

Technical and non-technical people, inside and outside of the immediate software develop- ment team.
Context 12

## Required

Yes, all software guidebooks should include an initial context section to set the scene.

## 2. Functional Overview

Functional Overview
Even though the purpose of a software guidebook isn’t to explain what the software does in detail, it can be useful to expand on the context and summarise what the major functions of the software are.

## Intent

This section allows you to summarise what the key functions of the system are. It also allows you to make an explicit link between the functional aspects of the system (use cases, user stories, etc) and, if they are significant to the architecture, to explain why. A functional overview should answer the following types of questions:

- Is it clear what the system actually does?
- Is it clear which features, functions, use cases, user stories, etc are significant to the
architecture and why?
- Is it clear who the important users are (roles, actors, personas, etc) and how the system
caters for their needs?
- It is clear that the above has been used to shape and define the architecture?
Alternatively, if your software automates a business process or workflow, a functional view should answer questions like the following:
- Is it clear what the system does from a process perspective?
- What are the major processes and flows of information through the system?

## Structure

By all means refer to existing documentation if it’s available; and by this I mean functional specifications, use case documents or even lists of user stories. However, it’s often useful to summarise the business domain and the functionality provided by the system. Again, diagrams can help, and you could use a UML use case diagram or a collection of simple

Functional Overview 14 wireframes showing the important parts of the user interface. Either way, remember that
the purpose of this section is to provide an overview.
Alternatively, if your software automates a business process or workflow, you could use a flow chart or UML activity diagram to show the smaller steps within the process and how they fit together. This is particularly useful to highlight aspects such as parallelism, concurrency, where processes fork or join, etc.

## Motivation

This doesn’t necessarily need to be a long section, with diagrams being used to provide an overview. Where a context section summarises how the software fits into the existing environment, this section describes what the system actually does. Again, this is about providing a summary and setting the scene rather than comprehensively describing every user/system interaction.

## Audience

Technical and non-technical people, inside and outside of the immediate software develop- ment team.

## Required

Yes, all software guidebooks should include a summary of the functionality provided by the software.

## 3. Quality Attributes

Quality Attributes
With the functional overview section summarising the functionality, it’s also worth includ- ing a separate section to summarise the quality attributes/non-functional requirements.

## Intent

This section is about summarising the key quality attributes and should answer the following types of questions:

- Is there a clear understanding of the quality attributes that the architecture must satisfy?
- Are the quality attributes SMART (specific, measurable, achievable, relevant and timely)?
- Havequalityattributesthatareusuallytakenforgrantedbeenexplicitlymarkedasout of scope if they are not needed? (e.g. “user interface elements will only be presented in English” to indicate that multi-language support is not explicitly catered for)
- Areanyofthequalityattributesunrealistic?(e.g.true24x7availabilityistypicallyvery costly to implement inside many organisations)
In addition, if any of the quality attributes are deemed as “architecturally significant” and therefore influence the architecture, why not make a note of them so that you can refer back to them later in the document.

## Structure

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

## 4. Constraints

Software lives within the context of the real-world, and the real-world has constraints. This section allows you to state these constraints so it’s clear that you are working within them and obvious how they affect your architecture decisions.

## Intent

Constraints are typically imposed upon you but they aren’t necessarily “bad”, as reducing the number of available options often makes your job designing software easier. This section allows you to explicitly summarise the constraints that you’re working within and the decisions that have already been made for you.

## Structure

As with the quality attributes, simply listing the known constraints and briefly summarising them will work. Example constraints include:

- Time, budget and resources.
- Approved technology lists and technology constraints.
- Target deployment platform.
- Existing systems and integration standards.
- Local standards (e.g. development, coding, etc).
- Public standards (e.g. HTTP, SOAP, XML, XML Schema, WSDL, etc). -  Standard protocols.
- Standard message formats.
- Size of the software development team.
- Skill profile of the software development team.
- Nature of the software being built (e.g. tactical or strategic).
- Political constraints.
- Use of internal intellectual property.
- etc

If constraints do have an impact, it’s worth summarising them (e.g. what they are, why they are being imposed and who is imposing them) and stating how they are significant to your architecture.

## Motivation

Constraints have the power to massively influence the architecture, particularly if they limit the technology that can be used to build the solution. Documenting them prevents you having to answer questions in the future about why you’ve seemingly made some odd decisions.

## Audience

The audience for this section includes everybody involved with the software development process, since some constraints are technical and some aren’t.

## Required

Yes, all software guidebooks should include a summary of the constraints as they usually shape the resulting software architecture in some way. It’s worth making these constraints explicit at all times, even in environments that have a very well known set of constraints (e.g. “all of our software is ASP.NET against a SQL Server database”) because constraints have a habit of changing over time.

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

## 6. Software Architecture

The software architecture section is your “big picture” view and allows you to present the structure of the software. Traditional software architecture documents typically refer to this as a “conceptual view” or “logical view”, and there is often confusion about whether such views should refer to implementation details such as technology choices.

## Intent

The purpose of this section is to summarise the software architecture of your software system so that the following questions can be answered:

- What does the “big picture” look like?
- Is there are clear structure?
- Is it clear how the system works from the “30,000 foot view”?
- Does it show the major containers and technology choices?
- Does it show the major components and their interactions?
- Whatarethekeyinternalinterfaces?(e.g.awebservicebetweenyourwebandbusiness
tiers)

## Structure

I use the container and component diagrams as the main focus for this section, accompanied by a short narrative explaining what the diagram is showing plus a summary of each container/component.
Sometimes UML sequence or collaboration diagrams showing component interactions can be a useful way to illustrate how the software satisfies the major use cases/user stories/etc. Only do this if it adds value though and resist the temptation to describe how every use case/user story works!

## Motivation

The motivation for writing this section is that it provides the maps that people can use to get an overview of the software and help developers navigate the codebase.

## Audience

The audience for this section is predominantly the technical people in the software develop- ment team.

## Required

Yes, all software guidebooks should include a software architecture section because it’s essential that the overall software structure is well understood by everybody on the development team.

## 7. Code

Although other sections of the software guidebook describe the overall architecture of the software, often you’ll want to present lower level details to explain how things work. This is what the code section is for. Some software architecture documentation templates call this the “implementation view” or the “development view”.

## Intent

The purpose of the code section is to describe the implementation details for parts of the software system that are important, complex, significant, etc. For example, I’ve written about the following for software projects that I’ve been involved in:

- Generating/rendering HTML: a short description of an in-house framework that was created for generating HTML, including the major classes and concepts.
- Data binding: our approach to updating business objects as the result of HTTP POST requests.
- Multi-page data collection: a short description of an in-house framework we used for building forms that spanned multiple web pages.
- Web MVC: an example usage of the web MVC framework that was being used.
- Security:ourapproachtousingWindowsIdentityFoundation(WIF)forauthentication
and authorisation.
- Domain model: an overview of the important parts of the domain model.
- Component framework: a short description of the framework that we built to allow
components to be reconfigured at runtime.
- Configuration: a short description of the standard component configuration mecha-
nism in use across the codebase.
- Architectural layering: an overview of the layering strategy and the patterns in use to
implement it.
- Exceptionsandlogging:asummaryofourapproachtoexceptionhandlingandlogging
across the various architectural layers.
- Patterns and principles: an explanation of how patterns and principles are imple-
mented.
- etc

## Structure

Keep it simple, with a short section for each element that you want to describe and include diagrams if they help the reader. For example, a high-level UML class and/or sequence diagram can be useful to help explain how a bespoke in-house framework works. Resist the temptation to include all of the detail though, and don’t feel that your diagrams need to show everything. I prefer to spend a few minutes sketching out a high-level UML class diagram that shows selected (important) attributes and methods rather than using the complex diagrams that can be generated automatically from your codebase with UML tools or IDE plugins. Keeping any diagrams at a high-level of detail means that they’re less volatile and remain up to date for longer because they can tolerate small changes to the code and yet remain valid.

## Motivation

The motivation for writing this section is to ensure that everybody understands how the important/significant/complex parts of the software system work so that they can maintain, enhance and extend them in a consistent and coherent manner. This section also helps new members of the team get up to speed quickly.

## Audience

The audience for this section is predominantly the technical people in the software develop- ment team.

## Required

No, but I usually include this section for anything other than a trivial software system.

## 8. Data

The data associated with a software system is usually not the primary point of focus yet it’s arguably more important than the software itself, so often it’s useful to document something about it.

## Intent

The purpose of the data section is to record anything that is important from a data perspective, answering the following types of questions:

- What does the data model look like?
- Where is data stored?
- Who owns the data?
- How much storage space is needed for the data? (e.g. especially if you’re dealing with
“big data”)
- What are the archiving and back-up strategies?
- Are there any regulatory requirements for the long term archival of business data? -  Likewise for log files and audit trails?
- Are flat files being used for storage? If so, what format is being used?

## Structure

Keep it simple, with a short section for each element that you want to describe and include domain models or entity relationship diagrams if they help the reader. As with my advice for including class diagrams in the code section, keep any diagrams at a high level of abstraction rather than including every field and property. If people need this type of information, they can find it in the code or database (for example).

## Motivation

The motivation for writing this section is that the data in most software systems tends to outlive the software. This section can help anybody that needs to maintain and support the data on an ongoing basis, plus anybody that needs to extract reports or undertake business intelligence activities on the data. This section can also serve as a starting point for when the software system is inevitably rewritten in the future.

## Audience

The audience for this section is predominantly the technical people in the software develop- ment team along with others that may help deploy, support and operate the software system.

## Required

No, but I usually include this section for anything other than a trivial software system.

## 9. Infrastructure Architecture

While most of the software guidebook is focussed on the software itself, we do also need to consider the infrastructure because software architecture is about software and infrastructure.

## Intent

This section is used to describe the physical/virtual hardware and networks on which the software will be deployed. Although, as a software architect, you may not be involved in designing the infrastructure, you do need to understand that it’s sufficient to enable you to satisfy your goals. The purpose of this section is to answer the following types of questions:

- Is there a clear physical architecture?
- What hardware (virtual or physical) does this include across all tiers?
- Does it cater for redundancy, failover and disaster recovery if applicable?
- Is it clear how the chosen hardware components have been sized and selected?
- If multiple servers and sites are used, what are the network links between them?
- Who is responsible for support and maintenance of the infrastructure?
- Are there central teams to look after common infrastructure (e.g. databases, message
buses, application servers, networks, routers, switches, load balancers, reverse proxies,
internet connections, etc)?
- Who owns the resources?
- Are there sufficient environments for development, testing, acceptance, pre-produc-
tion, production, etc?

## Structure

The main focus for this section is usually an infrastructure/network diagram showing the various hardware/network components and how they fit together, with a short narrative to accompany the diagram. If I’m working in a large organisation, there are usually infrastructure architects who look after the infrastructure architecture and create these diagrams for me. Sometimes this isn’t the case though and I will draw them myself.

## Motivation

The motivation for writing this section is to force me (the software architect) to step outside of my comfort zone and think about the infrastructure architecture. If I don’t understand it, there’s a chance that the software architecture I’m creating won’t work or that the existing infrastructure won’t support what I’m trying to do.

## Audience

The audience for this section is predominantly the technical people in the software develop- ment team along with others that may help deploy, support and operate the software system.

## Required

Yes, an infrastructure architecture section should be included in all software guidebooks because it illustrates that the infrastructure is understood and has been considered.

## 10. Deployment

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

## 11. Operation and Support

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

## 12. Development Environment

The development environment section allows you to summarise how people new to your team install tools and setup a development environment in order to work on the software.

## Intent

The purpose of this section is to provide instructions that take somebody from a blank operating system installation to a fully-fledged development environment.

## Structure

The type of things you might want to include are:

- Pre-requisite versions of software needed.
- Links to software downloads (either on the Internet or locally stored).
- Links to virtual machine images.
- Environment variables, Windows registry settings, etc.
- Host name entries.
- IDE configuration.
- Build and test instructions.
- Database population scripts.
- Usernames,passwordsandcertificatesforconnectingtodevelopmentandtestservices. -  Links to build servers.
- etc
If you’re using automated solutions (such as Vagrant, Docker, Puppet, Chef, Rundeck, etc), it’s still worth including some brief information about how these solutions work, where to find the scripts and how to run them.

## Motivation

The motivation for this section is to ensure that new developers can be productive as quickly as possible.

## Audience

The audience for this section is the technical people in the software development team, especially those who are new to the team.

## Required

Yes, because this information is usually lost and it’s essential if the software will be maintained by a different set of people from the original developers.

## 13. Decision Log

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
