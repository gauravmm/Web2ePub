"""
Publisher
Given a output from the scraper, produces output as an ePub file. Supports
styling using plugins.

@author: GauravManek
"""
import zipfile, uuid;
from os import path;
from time import strftime, gmtime;
from styling import getstyle;
from bs4 import BeautifulSoup as bs4;

# Aribtrary UUID used as the parent for all generated books:
PUBLISHER_NAMESPACE = uuid.UUID('926dda03-c0f7-4bed-9c97-6652a7ae3361');
# Creation Timestamp 
PUBLISHER_TIMEFT = "%Y-%m-%dT%H:%M:%SZ" # CCYY-MM-DDThh:mm:ssZ
PUBLISHER_TIME = lambda : strftime(PUBLISHER_TIMEFT, gmtime());

OEBPS = "OEBPS/";

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


def buildTOCInner(chapterList):
    # Assemble the TOC as a page.
    toc  = "<nav epub:type=\"toc\" id=\"toc\"><ol>\n";
    toc += "\n".join("<li><a href=\"" + fn + "\">" + name + "</a></li>" for fn, data, name, id, opt in chapterList);
    toc += "\n</ol></nav>";
    return toc;

MIMELookup = {".html": "text/html", ".css": "text/css", ".jpg": "image/jpeg",
              ".gif": "image/gif", ".png": "image/png", ".svg": "iamge/svg+xml"};
def getMIMEFromFn(fn):
    fnb, ext = path.splitext(fn);
    ext = ext.lower();
    if ext not in MIMELookup:
        print "Unrecognized MIME for file \"" + fn + "\"";
        return "application/dunno";
    else:
        return MIMELookup[ext];

# Build the all-important "OEBPS/content.opf" file.
def buildOPF(uid, modtime, bookmeta, filelist, spinelist):
    # First, the package element.
    soup = bs4(features='xml');

    # Set up shorthand to add an element with some contents:
    def soup_tag(a, v, c):
        rv = soup.new_tag(a, **v);
        rv.append(c);
        return rv;
    
    package = soup.new_tag("package", **{
        "xmlns": "http://www.idpf.org/2007/opf", 
        "version": "3.0", 
        "unique-identifier": "pub-id"
    });
    soup.append(package);

    # Metadata is the first required element of package.
    metadata = soup.new_tag("metadata", **{"xmlns:dc":"http://purl.org/dc/elements/1.1/"});
    # Its children are, in any order: 
    # dc:identifier [required],
    metadata.append(soup_tag("dc:identifier", {"id": "pub-id"}, uid));
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
    package.append(metadata);
    
    # Manifest is the second.
    manifest = soup.new_tag("manifest");
    for fn, data, name, id, opt in filelist:
        v = {"id": id, "href":fn, "media-type": getMIMEFromFn(fn)}
        # We need to indicate the TOC as the primary nav element.
        if "nav" in opt and opt["nav"]:
            v["properties"] = "nav"; 
        manifest.append(soup.new_tag("item", **v));
    package.append(manifest);

    # Spine is the third.
    spine = soup.new_tag("spine");
    for fn, cont, name, id, opt in spinelist:
        # Start each chapter on a right page:
        v = {"properties": "page-spread-right", "idref": id};
        if "linear" in opt and not opt["linear"]:
            v["linear"] = "no";
        spine.append(soup.new_tag("itemref", **v));
    package.append(spine);

        
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
    htmlFn = lambda fn: "html/" + (("p" + str(fn)) if str(fn)[0].isdigit() else str(fn)) + ".html";
    # An in-order list of chapters in the book:
    # As a 5-tuple: Filename, content, Text title, id, additional properties
    chapterList = [(htmlFn(id), ch["content"], ch["name"], "c" + str(id), {}) for (id, ch) in chpt];
    
    styler = getstyle(style_devstr);
    if not styler:
        raise RuntimeError("Cannot find output style " + style_devstr + ".");
    print "Styling for " + styler.name + ".";
       
    if len(imgs) > 0:
        print "Images are not supported yet!";  
    
    # The cover and TOC
    cover = (htmlFn("cover"), styler.cover(meta), "Cover", "cover", {"linear": True});
    toc = (htmlFn("toc"), styler.contents(buildTOCInner(chapterList)),  "Table of Contents", "toc", {"linear": False, "nav": True});
    
    cssList = [("style.css", styler.css(), "Main Stylesheet", "style", {})];
    spineList = [cover, toc] + chapterList;
    imageList = [];    # TODO: Add every image to imageList;
    fileList = spineList + cssList + imageList;
    
    # Write the OPF file:
    opf = buildOPF(uid, modtime, meta, fileList, spineList);    
    
    try:
        # Now we write everything to the output file
        epb = initFile(fn);
        epb.writestr(OEBPS + "content.opf", opf);
        
        # Now, we write all the files:
        for fname, data, name, id, opt in fileList:
            epb.writestr(OEBPS + fname, data.encode('utf-8'));
    
    finally:
        # Close the file.
        epb.close();
    
    return True;