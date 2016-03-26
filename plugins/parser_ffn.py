import plugins;
from bs4 import BeautifulSoup as bs4;
from bs4 import NavigableString;
from bs4.dammit import EntitySubstitution

escapeHTML = (EntitySubstitution()).substitute_xml;      
         
class FFNetParser(plugins.BaseWebsiteParser):
    # Called in the initializer:
    def __init__(self):
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
        rv["attrib"] = "FanFiction.net";

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
        
        rv["title"] = escapeHTML(titlebar[0].get_text("", strip=True));
        rv["author"] = escapeHTML(titlebar[2].get_text("", strip=True));
        
        comment = [x for x in header.stripped_strings];
        rv["comment"] = escapeHTML("\n".join(" ".join(c) for c in [comment[0:3], comment[3:10]]))
        rv["name"] = escapeHTML(comment[-1]);
              
        # Flatten it into a single array
        rv["data"] = unicode("");
        lines = (self._processLine(i, ch) for i, ch in enumerate(soup.find('div', id='storycontent').children));
        for l in lines:
            rv["data"] += "\n" + l;
        
        # Do we need to insert a start-of-document title?
        if self._heuristicTitleState == 0:
            rv["data"] = "<h1>" + rv["name"] + "</h1>\n" + rv["data"];

        # Replace HTML Entities that BeautifulSoup can't seem to fix:
        rv["data"] = self._fixEntities(rv["data"]);
            
        return rv;

    _replacements = [("&hellip;", u"\u2026")];
    def _fixEntities(self, data):
        for fr, to in self._replacements:
            data = data.replace(fr, to);
        return data;

    def _processLine(self, i, ch):
        if isinstance(ch, NavigableString):
            if(len(str(ch).strip()) == 0):
                return "";
            else:
                return "<p>" + ch.prettify(formatter='minimal') + "</p>";
        else:
            if self._heuristicIsSeparator(ch):
                return "<hr />"; # We customize this in CSS.
            elif self._heuristicIsTitle(i, ch):
                h = "h" + str(self._heuristicTitleState);
                return unicode("<" + h + ">" + ch.get_text(" ", strip=True) + "</" + h + ">")
            else:
                return ch.prettify(formatter='minimal');
    
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

if __name__ == "plugins":
    plugins.register(FFNetParser());
