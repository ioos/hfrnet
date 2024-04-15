---
# Feel free to add content and custom Front Matter to this file.
# To modify the layout, see https://jekyllrb.com/docs/themes/#overriding-theme-defaults

title: Code
layout: home
---

# 7. Code

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
