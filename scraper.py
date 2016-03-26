"""
Scraper
Given a URL, finds a parser and scrapes the input, optionally caching it.

@author: GauravManek
"""
import os, requests, pickle, re;
from plugins import getParser;
from publisher import imagepath;

# For debugging purposes, this allows us to cache arbitrary scraper input.
# This means we can quickly test ePub output.
def scrape(url, styler, **varg):
    folder = "cache/";
    
    urlstr = re.sub("[^0-9a-zA-Z]", '_', str(".".join([url.netloc, url.path])));
    fn = folder + urlstr + ".pickle";
    if varg['cache'] and os.path.isfile(fn):
        print "\tFound " + str(urlstr) + " in cache.";
        with open(fn, 'rb') as f:
            return pickle.load(f);
    else:
        rv = scrape_nocache(url, styler);
        with open(fn, 'wb') as f:
            pickle.dump(rv, f);
        return rv;

# Scrape without a cache.
def scrape_nocache(url, styler, **varg):
    # Load the parser:
    parser = getParser(url);
    if not parser:
        raise RuntimeError("Cannot find a parser that supports this website.");
    
    print "\tScraping with " + parser.name + " parser";
    
    done = [];
    pages = [];
    images = [];
    queue = [parser.getIdFromUrl(url)];
    doc = {};
    
    while len(queue) > 0:
        # Get the URL from the ID:
        pid = queue.pop();
        
        # If we have already processed this, ignore it.
        if pid in done:
            continue;
        
        img_pre = imagepath(parser.getSimplePageId(pid));
        dl = parser.getUrlFromId(pid);
        print "\tDownloading " + dl;
        # Download dl
        req = requests.get(dl);

        # Ignore this if it is not downloaded correctly.
        done.append(pid);
        if (req.status_code != 200):
            continue;
        
        # We do not support pictures yet.
        rv = parser.parsePage(req.text, pid, img_pre, styler);
        # If rv is an error page, skip it.
        if not rv:
            continue;
        
        # Copy over properties to the global document, if necessary and available.
        for prop in ["title", "author", "comment", "attrib", "cover"]:
            if prop not in doc and prop in rv:
                doc[prop] = rv[prop];

        # Now we add the proximate pages to the queue:    
        queue.extend(rv["also"]);
        
        # Add this page with the sorting key:
        pages.append((rv["id"], {"id": rv["id"], "name": rv["name"], "content": rv["data"]}));

        if "images" in rv:
            for im in rv["images"]:
                images.append((im[0], img_pre + im[1]));
    
    return (doc, pages, images);