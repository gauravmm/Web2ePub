"""
Default Style.

@author: GauravManek
"""
from plugins import BaseStyle, register;
from publisher import imagepath;

class DefaultStyle(BaseStyle):
    def __init__(self):
        self.name = "Default";
        self.devstr = "def";

    def page(self, title, page):
        header = """<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head>
<title>""" + title + """</title>
<link href="../style.css" rel="stylesheet" type="text/css"/>
</head>
<body>
""";
        footer = """
</body>
</html>
""";
        return header + page + footer;

    def cover(self, bookmeta):
        # Assemble the cover page.
        if "cover" in bookmeta:
            return "<div id=\"cover_img\"><img src=\"%s\" alt=\"Cover\" /></div>" % (imagepath() + bookmeta['cover'][0]);
        else:
            return "<div id=\"cover\"><h1>%s</h1>\n<div>%s</div></div>" % (bookmeta["title"], bookmeta["author"]);
    
    def contents(self, inner):
        # Assemble the table-of-contents.
        return "<h1>Contents</h1>\n" + inner;
                
    def css(self):
        return """/* Basic CSS */
        body { margin: 5px; }
        nav#toc ol { list-style-type: none; }
        #cover_img {width: 100%; height: 95%; text-align:center;}
        #cover { text-align: center; width: 100%; height: 90%; border: thick solid black;}
        #cover h1 { padding-top: 100px; font-size: 200%; }
        #cover div { padding-top: 50px; font-style: italic; width: 100%; }
        """;

if __name__ == "plugins":
    register(DefaultStyle());
