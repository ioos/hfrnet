---
# Feel free to add content and custom Front Matter to this file.
# To modify the layout, see https://jekyllrb.com/docs/themes/#overriding-theme-defaults

title: Notes
layout: home
---

# Notes and Questions

Use this file as a catch all for TODO items and other questions while developing the documentation.  Eventually this will be deleted.

## Architecture Description Diagram Structure

architecure - top level dir for dsl
./users.dsl - list of all users for hfrnet
./workspace.dsl - model that includes all generic containers that are true in the as-is and to-be versions
./hfrnetv1p0 - Standalone model (no inheritance yet) showing what we understand about the system at SIO/NDBC
./hfrnetv2p0 - Standalone model (no inheritance yet) showing the current understanding of the new system with questions colored orange.
./adrs - Folder with Architecture decision records  (This might not work, might need to be ../docs/adrs for Jekyll to work)

Maybe as a first step, I should keep v1 and v2 separate and focus on the Jekyll site?

How does the NDBC Node differ from the SIO Node?

- There is processing at the NDBC node to populate the THREDDS server that differs slightly from the way SIO populates their THREDDS server.

I've gone about as far as I can go without diving in to the code.  time to push this up to github so I can look at it on my work computer where the code lives.

Find the markdown file I created based on the functional decomposition diagram and get it into this repository before it gets lost.

## Outstanding TODO Items

- [ ] Finish copying the Functional Decomposition from the drawio diagram to [hfrnet-functional-decomposition.md](./hfrnet-functional-decomposition.md)
- [ ] Finish organizing the user documentation from the Google Drive into [users.md](./users.md)
- [ ] Write up goals and constraints following the C4 book.  A section that outlines high level goals about how radar fits into future DMAC.  Cloud based.  Open Source.  R2O between NOAA and partners.  
- [ ] Let go of this being a before and after document and focus on the future.  Keep the docs focused on the current state and the future state.  Let go of the past.

## Questions for Tuesday Tag Ups

1. What are we doing to capture and document the discussion happening among the data flow team and Lianyuan?  That is useful information that will help us ensure the new design is efficient and not duplicative.
1. The [functional decomposition diagram](https://app.diagrams.net/#G1r16I-PBNeO3ndLxR620uVODlhzfEYOXA#%7B%22pageId%22%3A%22Wj2H4JzCPwmI87_5JtUa%22%7D) contains many functions or requirements that are not part of the present design or migration plan. How are we analyzing these and plannning for eventual implementation or elimination?
