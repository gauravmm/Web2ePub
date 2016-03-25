"""
Plugin Base
Contains base classes that must be extended when writing plugins.

Gaurav Manek
"""
import glob, sys;

#
# Plugin registration:
#

PLUGIN_DIR = "plugins/";
sys.path.append(PLUGIN_DIR);

parsers = [];
stylers = [];
covers = [];
global _attemptedRegistration;

def register(plugin):
    global _attemptedRegistration;
    _attemptedRegistration = True;
    if isinstance(plugin, BaseWebsiteParser):
        parsers.append(plugin);
    elif isinstance(plugin, BaseStyle):
        stylers.append(plugin);
    elif isinstance(plugin, BaseCover):
        covers.append(plugin);
    else:
        print "Plugin " + str(plugin) + " not recognized!";

def _getDevStr(arr, devstr):
    for s in arr:
        if devstr == s.devstr:
            return s;

getStyle = lambda devstr: _getDevStr(stylers, devstr);
getCover = lambda devstr: _getDevStr(covers, devstr);

def getParser(url):
    for p in parsers:
        if p.canParse(url):
            return p;

# Load all the plugins
def load():
    global _attemptedRegistration;
    ls = glob.glob(PLUGIN_DIR + "[!_]*.py");
    for l in ls:        
        _attemptedRegistration = False;
        execfile(l);
        if not _attemptedRegistration:
            print "Plugin file \"" + l + "\" loaded, but no plugin registered.";
            print "Did you forget to call plugin.register?";


#
# Various Base Classes:
#

# Base class for all website parsers.
class BaseWebsiteParser(object):
    # Called in the initializer:
    def __init__(self):
        self.name = "Template";
        pass;
        
    # Called with a urlparse object representing the input URL, return True if
    # this class can parse this URL.
    def canParse(self, url):
        return False;
    
    # Get a simple page id from a pid, used to identify pages internally for 
    # image separation.
    def getSimplePageId(self, pid):
        return;
        
    # Return a comparable object (i.e. int, string, or tuple of these, that 
    # uniquely identifies the page pointed to by the URL.
    def getIdFromUrl(self, url):
        return;

    # Return the URL of a page with the given id, used to download the page.
    def getUrlFromId(self, pid):
        return;
    
    # Given the source of a page, as a string, return a dict with the following
    # entries:
    #   rv["title"]  = The title of the file
    #   rv["author"] = The author of the file
    #   rv["cover"]  = The URL of the cover image
    #   rv["comment"]= Any additional comment/metadata to include.
    #   rv["name"]   = The title of the page, used in the spine/TOC.
    #   rv["data"]   = HTML source to put in the ePub, normalized (i.e. with 
    #                  <h1>Headers</h1>, <p>Paragraphs</p>, and <img />es). All 
    #                  images are to be directed to the image_prefix
    #   rv["images"] = Images to download, as (URL, target) tuples. When saving
    #                  all target names will have image_prefix prepended to 
    #                  them.
    #   rv["id"]     = A unique id to identify and sort the pages by. Must be
    #                  an int.
    #   rv["also"]   = A list of additional ids of pages to consider. This
    #                  can include duplicates and may include pages that do not
    #                  exist. You can pass the entire list of pages to this, or
    #                  just the adjacent pages.
    #
    # Or return None to ignore this page.
    #    
    # Called with:
    #   source       = A string containing the raw source of the page.
    #   image_prefix = A prefix to the basename of the image, if images are 
    #                  allowed. Otherwise, None.
    def parsePage(self, source, image_prefix):
        return False;


# Base class for all style
class BaseStyle(object):
    def __init__(self):
        # A short string used to report this name in the style.
        self.name = "Base Style";
        # A short string used to identify this styling option in the commandline.
        self.devstr = "abc";

    # Produces the full markup for a content page, given:
    #   title = The page title, as a string.
    #   page  = The inner markup of the page, as a string.
    def page(self, title, page):
        return title + " " + page;
    
    # Produces the markup for the cover, given:
    #   bookmeta = The book metadata.
    def cover(self, bookmeta):
        # Assemble the cover page.
        return "<div id=\"cover\"><h1>%s</h1>\n<div>%s</div></div>" % (bookmeta["title"], bookmeta["author"]);
    
    # Produces the markup for the table of contents, given:
    #   inner = The inner markup for the TOC. By the specification, this should
    #           not be altered in any way.
    def contents(self, inner):
        return "<h1>Contents</h1>\n" + inner;

    # Produces a list of (filename, imagedata) pairs, given:
    #   bookmeta = The book metadata.
    # The provided images are written to the epub in the ../images/ folder
    # relative to all markers.
    def images(self, bookmeta):
        return [];
    
    # Return the contents of style.css
    #   bookmeta = The book metadata.
    def css(self, bookmeta):
        return "/* Basic CSS */";


# Base class for all coverpage generators.
class BaseCover(object):
    def __init__(self):
        # A short string used to report this name in the style.
        self.name = "Base Cover";
        # A short string used to identify this styling option in the commandline.
        # Does not have to be different than the Style devstr
        self.devstr = "abc";

    # Produces a (ext, data) tuple, given:
    #   bookmeta = The book metadata.
    #
    # The output is:
    #   ext  = File extension of data, which must be supported by the ePub standard.
    #   data = Image Data.
    def cover(self, bookmeta):
        return ("svg", "<svg></svg>");
