---
# Feel free to add content and custom Front Matter to this file.
# To modify the layout, see https://jekyllrb.com/docs/themes/#overriding-theme-defaults

title: Functional Overview
layout: home
---

# 2. Functional Overview


[FDD](./hfrnet-functional-decomposition)

Even though the purpose of a software guidebook isn’t to explain what the software does in detail, it can be useful to expand on the context and summarise what the major functions of the software are.
Intent
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

By all means refer to existing documentation if it’s available; and by this I mean functional specifications, use case documents or even lists of user stories. However, it’s often useful to summarise the business domain and the functionality provided by the system. Again, diagrams can help, and you could use a UML use case diagram or a collection of simple wireframes showing the important parts of the user interface. Either way, remember that
the purpose of this section is to provide an overview.
Alternatively, if your software automates a business process or workflow, you could use a flow chart or UML activity diagram to show the smaller steps within the process and how they fit together. This is particularly useful to highlight aspects such as parallelism, concurrency, where processes fork or join, etc.

## Motivation

This doesn’t necessarily need to be a long section, with diagrams being used to provide an overview. Where a context section summarises how the software fits into the existing environment, this section describes what the system actually does. Again, this is about providing a summary and setting the scene rather than comprehensively describing every user/system interaction.

## Audience

Technical and non-technical people, inside and outside of the immediate software develop- ment team.

## Required

Yes, all software guidebooks should include a summary of the functionality provided by the software.
