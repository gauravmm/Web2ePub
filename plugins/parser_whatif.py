import plugins;
from bs4 import BeautifulSoup as bs4;
from bs4 import NavigableString;
from bs4.dammit import EntitySubstitution

escapeHTML = (EntitySubstitution()).substitute_xml;      
                 
class WhatIfXKCDParser(plugins.BaseWebsiteParser):
    # Called in the initializer:
    def __init__(self):
        pass;
        
    # Called with a urlparse object representing the input URL, return True if
    # this class can parse this URL.
    def canParse(self, url):
        return False;
        

    def parsePage(self, source, image_prefix):
        return False;
        
if __name__ == "plugins":
	plugins.register(WhatIfXKCDParser());