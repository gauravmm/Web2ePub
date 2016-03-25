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
        header = """<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
<head>
<title>""" + book['title'] + ": " + page['name'] + """</title>
<link href="../styles/main.css" rel="stylesheet" type="text/css"/>
</head>
<body>
""";

        footer = """
</body>
</html>
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
    