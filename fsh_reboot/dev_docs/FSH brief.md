agenda:
make up notes to send round
look at icons/ buttons
the exhibition text


notes

notes for meeting 13th November

Typesetting:
C will make three versions for internal signoff: wall, web and web easy
C will make up full set of text files as they are, it would be best if amends were made to this text file, and then final text can be flowed into all versions
Initial set will be 
- Dr Johnson
- Magpie Alley
- The News Chronicle

Plan for web display is that we will either have a multi-page pdf only displaying first page, or will have a link to further info on the web page leading to notes that will only show on web. L has checked and both look viable, but L prefers 1 page pdf approach.

To check - will audio only be of natural language version? Should the audio links show on easy read page in the same way?

Next week: 
L will have shared schematic of web elements, L and C will have discussed and we can see first draft of visual design for web elements


typesetting:
first step - make up corpus of all text files, with over/under word count text estimate from quick rough flow
start with first three
- Dr Johnson
- Magpie Alley
- The News Chronicle

two text files - og and edit
three layouts - nl wall ceramic, nl web, er web

to check - is it possible to only display first page of pdf in wrapper - if so we will have second page on every pdf, with full copyright and any additional notes

wall: invitation
web - will have buttons above


change buttons to explain the different versions
just doing audio of natural language version?
on final setting remove all double spaces



ask a question


meeting  notes 

is text final, does it need a final proofread
yes, veronica and gillian
is the sidebar text final, does that need a re-edit - it does
we will start with three - dr johnson, magpie alley, the news chronicle
redraft suggestions for rhc
lets have a next and previous - yes ln needs to think about
natural language by default - yes

notes of decisions

page-panels
- change to having one qr code per page-panel rather than two
- remove cc notice at bottom of each page-panel (and move to single notice on right hand panel) - will have tiny half line on web versions 
- use space created to increase font size on all page panels 
- consider adding category link qr codes to the red header bars - would need some page/ view to land on

web
- allow for navigation from the single qr code, user can choose easy/ natural after landing on first target page
- design for 'first view' to be bigger/ clearer, can be smaller on future visits (visits per machine)
- make up a set of usable urls that are word-based/ human readable rather than number based (whether canonical or not)

plan:
- make a schematic user flow, with one example final design for each touchpoint (L and C to collaborate), 2 week deadline
- qr codes for this schematic do not need to be functional, if they do anything then plan to make holding page/view
- (in later conversation L and C agreed that doing 3 examples would be better)

future, when waters calm:
- consider introducing a navigation page on web that shows a 'map' of the wall, so people can navigate as though in front of the wall



chat on Oct 23

decisions:

increase font size on panels
remove cc notice, move to rh panel
one 2d barcode per page
one qr code per panel

make a schematic flow for the whole experience - 3
nfc tag behind/ close to rh panel
parallel set of links



make example


nfc (rain proof, must be locked so unhackable)
single panel for accessiblity - 1 of 4 or another, perhps on/ around elec box
futureproofing - what when there are new tech, best to change 1 panel
intermediary nav page could show map of all pages with headlines, could be mirrored on web
header bar bigger on first visit
ln to make schematic of header bar


quick links written
potential short url domain

nav page could have key, titles, individual urls

visual interest could be added with background print of famous headlines etc

main plan wrapper:
do wrapper page with header bar - natural, easy, audio controls
header bar with easy choice is big on first use, small after that
pages will have aria-labelled links
tracking of source by query string
first choice big and then small for future switches
easy/ natural prefs stored in local.storage or cookies to maintain prefs *per machine*
could have a link to put in an email reminder - enter your email here to be informed when new pages are made

main plan qr code
qr code (and possibly nfc) to address urls uniquely - initially set up to be per page but *could be changed later*
also contain query string to id referent - the wall/ the web pdfs/ etc


qr codes have query string which ids source - one for wall and one for web pdfs at the moment


decision: switch to names
decision: remove cc notice 

nfc
new nav page with map and titles and links




---



qs
number of pages 96
3- 9
2- 19
1 the rest
number of easy read pages 3/ 86 - 89
london living wage - 
qr codes


  

# Fleet Street Heritage – Web Development Brief

  

**Project Title:** Accessibility Upgrade & PDF Wrapper Deployment  

**Client:** Fleet Street Heritage  

**Date:** 12 May 2025

  

---

  

## Project Overview

  

Fleet Street Heritage is a digital archive currently hosting over 200 direct PDF links, which are not easily accessible, navigable, or traceable with analytics. 

This project will wrap each PDF in a custom HTML page, introduce accessible Easy Read versions of the content (developed separately), and audio narrated version of each page. Analytics will be configured to provide insights into user engagement and origin of visits.

Creation of the **Natural Language versions** and **Audio narration versions** of the content **not in scope** for this brief.

  

---

  

## Objectives

  
- Improve access and navigation by creating HTML wrapper pages for all PDFs.

- Create navigation and logic to allow users to access Natural Language and Easy Read versions of each page (developed separately)

- Create audio controls to allow users to access Audio narration versions of each page (developed separately), without a download-to-disk link.

- Ensure Easy Read/ natural language navigation is persistent and intuitive.

- Set up Google Analytics for aggregated insight by content group.

- Deliver a page structure that supports future expansion and consistent design.

---

  

## Deliverables

  

### 1. HTML Wrapper Pages (100 Total)

  

Each existing PDF will be wrapped in a new HTML wrapper page that includes:

- Fleet Street Heritage title bar in the natural language version

	- Home button
	
	- Embedded audio controls for narrated text (no download option)
	
	- Toggle link to Easy Read version of the same content
	
	- Navigation logic that maintains Natural language pathway unless user switches back to Natural Language mode

In addition, a code block will be supplied to enable analytics through google analytics

This will be developed with mock design and provided to Clare for visual design treatment. Design assets from Clare will be reintegrated to achieve final design intent.

These wrapper pages will **not** include the full Natural Language content in HTML — they will include the PDF itself, any metadata provided, link to easy-read page (if provided), and controls for audio (if provided).

  

### 2. Easy Read Pages (100 Total)

- Each easy read page will be topped with the new Fleet Street Heritage title bar, in the easy read version

	- Home button
	
	- Embedded audio controls for narrated text (no download option)
	
	- Toggle link to Natural Language version of the same content
	
	- Navigation logic that maintains Natural Language pathway unless user switches back to Natural Language mode

 In addition, a code block will be supplied to enable analytics through google analytics

  

### 3. Easy Read Navigation Logic

  

- Once a user accesses an Easy Read page, all internal links will route to other Easy Read pages, the same will be true for Natural Language pages

- A clear toggle will allow switching between Natural Language and Easy Read content

- All navigation behaviors will be consistent across the site

  

### 4. Analytics Configuration

  

- Google Analytics integrated across all wrapper and Easy Read pages

- Aggregated reporting for content grouped into:

  - 1xx pages

  - 2xx pages

  - 3xx pages

- Event tracking for:

  - Audio engagement

  - Easy Read usage

  - Page views, bounce rates, and navigation paths

  - Origins - links, qr codes, the Heritage Wall, leaflets etc.

  

### 5. Integration of Visual Design

  

- Will supply structure of header bar for visual design and receive in return a visual design mockup and asset set from Clare (designer)

- Title bar and branding to be applied consistently across all pages, with a different look to at least the toggle link on Natural Language pages and Easy Read pages

- Layouts to be responsive and accessible 

  

---

  

## Technical Specifications

  

- HTML5, CSS3, and vanilla JavaScript for interactivity and audio control

- Static site architecture (no backend or CMS)

- SEO metadata and accessibility tags included (if supplied)

- Mobile- and screen-reader-friendly structure

  

---

  



## Budget Estimate (Simplified – Expressed in Hours)

This section reflects effort in estimated hours per task. No hourly rate or cost is included.

| Task                                      | Estimated Hours |
|-------------------------------------------|------------------|
| Project setup and analytics config        | 12 hours         |
| Page structure + header dev               | 32 hours         |
| Build 200 wrapper pages                   | 8 hours          |
| Create/populate 200 Easy Read pages       | 16 hours         |
| Embed and test audio playback             | 8 hours          |
| QA, testing, and analytics verification   | N/A              |
| Handover and documentation                | N/A              |

  

---

  

## Cost Estimate (Based on Moderate Commercial Rates)

| Task                                    | Estimated Hours | Rate (£/hr) | Subtotal (£) |
| --------------------------------------- | --------------- | ----------- | ------------ |
| Project setup and analytics config      | 12 hours        | £55         | £660         |
| Page structure + header dev             | 32 hours        | £50         | £1,600       |
| Build 200 wrapper pages                 | 8 hours         | £50         | £400         |
| Create/populate 200 Easy Read pages     | 16 hours        | £50         | £800         |
| Embed and test audio playback           | 8 hours         | £50         | £400         |
| QA, testing, and analytics verification | 0 hours         | £0          | £0           |
| Handover and documentation              | 0 hours         | £0          | £0           |
| **Contingency (10%)**                   | —               | —           | **£386**     |

**Total Estimate: £4,246**

  

---

  

## Exclusions & Assumptions

  

- **Natural Language content templating and Audio file generation is out of scope** and will be created by the Fleet Street Heritage team.
