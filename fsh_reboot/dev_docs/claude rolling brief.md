20260403

hi we have a website to build. summary brief is in this folder. It's an iteration of a public information site about the history of Fleet Street (the old newspaper district of London). The old site is a hand-rolled static html site, with just a few html pages for navigation and almost all the content presented in pdfs that load directly into the browser, so no control or analytics. 

That site is in ../docs where there is a lot of mess, mostly in the pdfs, just have a look at index.html and maybe glance at a few  others. We are planning to load pdfs into wrapper pages, there will also be audio equivalent sound files and 'easy read' versions for accessibility, and the wrapper pages will provide navigation to these. The wrapper pages will also allow us to add analytics hooks so we can see how people are using the site, and we'll be making a qr code system to allow users to easily access the right part of the website from qr codes on leaflets, posters, flyers and a public exhibition, again with good analytics. Accessiblilty is important and we want to follow best practices.


Qs from Claude
  ---
  Blocking — I need these to proceed:                                                   
                                                                                        
  1. Content data / page list — Is there a spreadsheet or structured list mapping page
  numbers to titles, slugs, categories, and which pages have Easy Read / audio          
  available? I can extract the titles from index.html but a canonical list would be much
   better. This is the foundation for templating and URL generation.

   > this is coming, for now index.html is the best guide

  2. URL structure — The brief says "word-based / human-readable URLs". Has a slug
  scheme been decided? e.g. /dr-johnson/, /pages/dr-johnson/, or something else? And are
   these canonical URLs or do the numbered pages stay and these are redirects?

   > we can decide this

  3. Folder/deployment structure — Does the new site replace docs/ entirely, or live in 
  fsh_reboot/ alongside it? What's the deployment target (GitHub Pages, the existing    
  hosting, something else)? This affects all relative paths.

  > existing hosting is github pages, our new site will replace the old one in due course, until then (once we have something to test) we will test it either in a subfolder or on a separate testing repo - we can choose
                                                                                        
  ---             
  Design/content — worth clarifying now:
                                                                                        
  4. Missing Easy Read PDFs / audio — Since these are being created separately, how
  should wrapper pages behave before they exist? Hide the toggle entirely, or show it   
  greyed out / "coming soon"?

  > i think let's be adaptive and if the content is missing we don't show the control, if it is we do

  5. Easy Read content format — E_150.html currently loads the same 150.pdf. Will Easy  
  Read versions be separate PDFs (e.g. E_150.pdf), or HTML content directly on the page?

  > what would be best for accessibility?

  6. Navigation order — Prev/next between pages: is this numerical order within a
  volume, or the same order as the index page listing?   

  > most likely following the index page. we can design this. Also there is the idea of a spatial naviation interface - most of the pages are also presented as printed ceramic tiles on the real-life wall in Fleet street, and we might make an interface to move around these pages as though in front of the wall                               
                  
  ---                                                                                   
  Technical — I can propose defaults but worth confirming:
                                                                                        
  7. QR source identifiers — Has a set of query string values been agreed for tracking
  source? e.g. ?src=wall, ?src=leaflet, ?src=web? Or do I propose these?
  > these are not finalised, let's start a doc with specs that we can populate as we agree them                
  8. Accessibility target — Assuming WCAG 2.1 AA as the standard (appropriate for a
  public interest site). Correct?
  > I don't know, if that's your recommendation for UK public sector then great let's do that.                                                       
  9. "First visit" scope — The brief says the header should be large on first visit. Is
  this per-page or site-wide? i.e. once you've visited any page, the header shrinks     
  everywhere, or does it shrink per-page independently? 
  > site wide
                                                                                        
  ---             
  The single most useful thing would be the content/page list (question 1) — everything
  else I can either make reasonable assumptions about or we can decide together.        