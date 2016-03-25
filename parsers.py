from bs4 import BeautifulSoup as bs4;
from bs4 import NavigableString;

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
        
         
class FFNetParser(BaseWebsiteParser):
    # Called in the initializer:
    def __init__(self):
        super(FFNetParser,self).__init__();
        self.name = "FanFiction.net";
        
    def canParse(self, url):
        if url.netloc in ["www.fanfiction.net", "m.fanfiction.net"]:
            pid = url.path.split('/');
            if(pid[2] != "" and int(pid[2])):
                return True;
    
    def getSimplePageId(self, pid):
        return pid[1];
    
    def getIdFromUrl(self, url):
        psplit = url.path.split('/');
        if(len(psplit) > 2):
            return (psplit[2], int(psplit[3]));
        else:
            return (psplit[2], 1);

    def getUrlFromId(self, pid):
        return "http://m.fanfiction.net/s/" + pid[0] + "/" + str(pid[1]);
        
    def parsePage(self, source, pid, image_prefix):
        rv = {};
        rv["id"] = pid[1];

        # We add the links here, knowing only the page id:
        rv["also"] = [(pid[0], pid[1] + 1), (pid[0], 1)];
        
        soup = bs4(source, "lxml");
        
        # Check for 404:
        errpg = soup.find('div', attrs={'class', 'panel'});
        if errpg:
            if "Chapter not found." in errpg.get_text("", strip=False):
                return None;

        # Parse the header for metadata:
        header = soup.find('div', id='content');    
        titlebar = header.find('div', align='center').contents;
        rv["title"] = titlebar[0].get_text("", strip=True);
        rv["author"] = titlebar[2].get_text("", strip=True);
        
        comment = [x for x in header.stripped_strings];
        rv["comment"] = "\n".join(" ".join(c) for c in [comment[0:3], comment[3:10]])
        rv["name"] = comment[-1];
              
        # Flatten it into a single array
        rv["data"] = "";
        lines = (self._processLine(i, ch) for i, ch in enumerate(soup.find('div', id='storycontent').children));
        for l in lines:
            rv["data"] += "\n" + l;
        
        # Do we need to insert a start-of-document title?
        if self._heuristicTitleState == 0:
            rv["data"] = "<h1>" + rv["name"] + "</h1>\n" + rv["data"];
            
        return rv;

    def _processLine(self, i, ch):
        if isinstance(ch, NavigableString):
            if(len(str(ch).strip()) == 0):
                return "";
            else:
                return "<p>" + unicode(ch) + "</p>";
        else:
            if self._heuristicIsSeparator(ch):
                return "<hr />"; # We customize this in CSS.
            elif self._heuristicIsTitle(i, ch):
                h = "h" + str(self._heuristicTitleState);
                return unicode("<" + h + ">" + ch.get_text(" ", strip=True) + "</" + h + ">")
            else:
                return unicode(ch);
    
    def _heuristicIsSeparator(self, ch):
        if(ch.name == "hr"):
            return True;
        
        if(ch.has_attr('style') and "text-align:center;" in ch['style']):
            t = ch.get_text("", strip=True);
            return len(t) < 7 or len(set(t)) < 5; 
            # If the candidate is short or if it has few unique characters, its
            # likely to be a separator.
        return False;
    
    def _heuristicIsTitle(self, i, ch):
        if i == 0:
            self._heuristicTitleState = 0;
        
        if (ch.has_attr('style') and "text-align:center;" in ch['style']):
            # If we don't find a bold, then its not a title
            # If we find a bold and italics, then something is being emphasized
            # and this is unlikely to be a title.    
            if not ch.find("strong") or ch.find("em"): 
                return False;
            
            if i < 10 and self._heuristicTitleState == 0:
                self._heuristicTitleState = 1;
            else:
                self._heuristicTitleState = 2;
            return True;
        
class WhatIfXKCDParser(object):
    # Called in the initializer:
    def __init__(self):
        super(WhatIfXKCDParser,self).__init__();
        pass;
        
    # Called with a urlparse object representing the input URL, return True if
    # this class can parse this URL.
    def canParse(self, url):
        return False;
        

    def parsePage(self, source, image_prefix):
        return False;
        
def getparser(url):
    for p in [FFNetParser(), WhatIfXKCDParser()]:
        if p.canParse(url):
            return p;
    return;