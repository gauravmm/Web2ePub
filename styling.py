"""
Styling
Styles specific to devices.

@author: GauravManek
"""

class StyleBase(object):
    def __init__(self):
        # A short string used to report this name in the style.
        self.name = "Default";
        # A short string used to identify this styling option in the commandline.
        self.devstr = "def";

    def page(self, book, page):
        header = """<!DOCTYPE html>
<head>
<title>""" + book['title'] + ": " + page['name'] + """</title>
<link href="../style.css" rel="stylesheet" type="text/css"/>
</head>
<body>
""";

        footer = """
</body>
</html>
""";

    def cover(self, bookmeta):
        # Assemble the cover page.
        return "<h1>%s</h1>\n<p><em>%s</em></p>" % (bookmeta["title"], bookmeta["author"]);
    
    def contents(self, inner):
        # Assemble the table-of-contents.
        return "<h1>Contents</h1>\n" + inner;
                
    def css(self):
        return """/* Basic CSS */
        body { margin: 5px; }
        """;
         


class StyleNookGP(StyleBase):
    def __init__(self):
        super(StyleNookGP,self).__init__();
        self.name = "Nook GlowLight Plus";
        self.devstr = "ngp";
        

def getstyle(devstr):
    for styler in [StyleBase(), StyleNookGP()]:
        if devstr == styler.devstr:
            return styler;
    