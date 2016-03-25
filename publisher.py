"""
Publisher
Given a output from the scraper, produces output as an ePub file. Supports
styling using plugins.

@author: GauravManek
"""
import zipfile, uuid;
from time import strftime, gmtime;
from styling import getstyle;
from bs4 import BeautifulSoup as bs4;

# Aribtrary UUID used as the parent for all generated books:
PUBLISHER_NAMESPACE = uuid.UUID('926dda03-c0f7-4bed-9c97-6652a7ae3361');
# Creation Timestamp 
PUBLISHER_TIMEFT = "%Y-%m-%dT%H:%M:%SZ" # CCYY-MM-DDThh:mm:ssZ
PUBLISHER_TIME = lambda : strftime(PUBLISHER_TIMEFT, gmtime());

# Given path p, produce a relative path to the images folder in an ePub file.
def imagepath(p):
    return "../images/" + str(p).replace("/", "_") + "/";


def initFile(fn):
    # Create the basic file. The default option is not to compress it, which is
    # exactly what we need. See https://en.wikipedia.org/wiki/EPUB for a quick
    # description, and http://idpf.org/epub for the spec.
    # Taking apart existing .epub files also helps.
    rv = zipfile.ZipFile(fn + ".zip", 'w');
    
    # The first file in the archive must be the mimetype file.
    rv.writestr("mimetype", "application/epub+zip");
    
    # Then we add container.xml, which points to the .opf file for the main 
    # and only Rendition.
    rv.writestr("META-INF/container.xml", """<?xml version="1.0" encoding="UTF-8" ?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>""");

    return rv;


def buildTOC(chpt, chapterFn):
    # Assemble the TOC as a page.
    toc  = "<nav epub:type=\"toc\" id=\"toc\"><ol>\n";
    toc += "\n".join("<li><a href=\"" + chapterFn(fn) + "\">" + ch["name"] + "</a></li>" for fn, ch in chpt);
    toc += "\n</ol></nav>";
    return {"id": "toc", "name": "Table of Contents", "contents":toc};

# Build the all-important "OEBPS/content.opf" file.
def buildOPF(uid, modtime, bookmeta):
    # First, the package element.
    soup = bs4(features='xml');

    # Set up shorthand to add an element with some contents:
    def soup_tag(a, v, c):
        rv = soup.new_tag(a, **v);
        rv.append(c);
        return rv;
    
    package = soup.new_tag("package", **{
        "xmlns": "http://www.idpf.org/2007/opf", 
        "version": "3.1", 
        "unique-identifier": str(uid)
    });
    soup.append(package);

    # Metadata is the first required element of package
    metadata = soup.new_tag("metadata", **{"xmlns:dc":"http://purl.org/dc/elements/1.1/"});
    # Its children are, in any order: 
    # dc:identifier [required],
    metadata.append(soup_tag("dc:identifier", {}, uid));
    # meta [1 or more],
    #   This particular property is used for versioning, and so is important:
    metadata.append(soup_tag("meta", {"property":"dcterms:modified"}, modtime));
    # dc:title [required],
    #   TODO: Heuristic-based file-as
    metadata.append(soup_tag("dc:title", {}, bookmeta["title"]));
    # dc:language [1 or more],
    #   TODO: Commandline switch to specify language.
    metadata.append(soup_tag("dc:language", {}, "en"));
    # dc:creator [0 or more],
    metadata.append(soup_tag("dc:creator", {}, bookmeta["author"]));
    # dc:type [0 or more],
    
    # link [0 or more]
    package.append(metadata);
    
    
    return soup.prettify();


def epub(inp, fn, style_devstr):
    # Split it into metadata, chapters, and images.    
    meta, chpt, imgs = inp;
    # Sort the chapters
    chpt.sort();

    # Prepare the UUID and the creation time:
    uid = str(uuid.uuid5(PUBLISHER_NAMESPACE, fn)); # Generate a file UUID
    modtime = PUBLISHER_TIME();    
    
    # From Chapter Number to filename:
    chapterFn = lambda fn: "p" + str(fn) + ".html";
    
    styler = getstyle(style_devstr);
    if not styler:
        raise RuntimeError("Cannot find output style " + style_devstr + ".");
    print "Styling for " + styler.name + ".";
    
    # Prepare the output file
    epb = initFile(fn);
    
    # Okay, now we add the actual files to the ePub, keeping track of them so
    # we can populate the manifest later.
    if len(imgs) > 0:
        print "Images are not supported yet!";  
    for fn, ch in chpt:
        pass;
  
    toc = buildTOC(chpt, chapterFn);
    opf = buildOPF(uid, modtime, meta);    
    
    print opf;    
        
