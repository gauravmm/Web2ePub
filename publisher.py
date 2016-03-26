"""
Publisher
Given a output from the scraper, produces output as an ePub file. Supports
styling using plugins.

Gaurav Manek
"""
import zipfile, uuid;
from os import path, remove;
from time import strftime, gmtime;
from plugins import getCover;
from bs4 import NavigableString;
from bs4 import BeautifulSoup as bs4;
from io import BytesIO;

# Aribtrary UUID used as the parent for all generated books:
PUBLISHER_NAMESPACE = uuid.UUID('926dda03-c0f7-4bed-9c97-6652a7ae3361');
# Creation Timestamp 
PUBLISHER_TIMEFT = "%Y-%m-%dT%H:%M:%SZ" # CCYY-MM-DDThh:mm:ssZ
PUBLISHER_TIME = lambda : strftime(PUBLISHER_TIMEFT, gmtime());

OEBPS = "OEBPS/";

# Given path p, produce a relative path to the images folder in an ePub file.
def imagepath(p=None):
    if p:
        return "../images/" + str(p).replace("/", "_") + "/";
    else:
        return "../images/";


def initFile(fn):
    # Create the basic file. The default option is not to compress it, which is
    # exactly what we need. See https://en.wikipedia.org/wiki/EPUB for a quick
    # description, and http://idpf.org/epub for the spec.
    # Taking apart existing .epub files also helps.
    rv = zipfile.ZipFile(fn, 'w');
    
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
    toc += "\n".join("<li><a href=\"../" + fn + "\">" + name + "</a></li>" for fn, data, name, id, opt in chapterList);
    toc += "\n</ol></nav>";
    return toc;


MIMELookup = {".xhtml": "application/xhtml+xml", ".html": "text/html", ".css": "text/css", ".jpg": "image/jpeg",
              ".gif": "image/gif", ".png": "image/png", ".svg": "image/svg+xml", ".ncx": "application/x-dtbncx+xml"};
def getMIMEFromFn(fn):
    fnb, ext = path.splitext(fn);
    ext = ext.lower();
    if ext not in MIMELookup:
        print "\tUnrecognized MIME for file \"" + fn + "\"";
        return "application/dunno";
    else:
        return MIMELookup[ext];


# Build the all-important "OEBPS/content.opf" file.
def buildOPF(uid, modtime, bookmeta, filelist, spinelist, imagelist):
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
    # Additional declaration, for backwards compatibility:
    # This is to make sure that devices correctly display the book cover art.
    if "cover" in bookmeta:
        covertag = soup.new_tag("meta");
        # Some readers, like the Nook, need the attributes to be in this
        # specific order. Apparently its against union rules to adopt the
        # basic assumption of XML attributes. I mean, why not just ignore
        # more conventions and wander into an intersection against traffic
        # and make humanity just a little happier?

        #covertag.attrs["name"]="cover";
        #covertag.attrs["content"]=bookmeta["cover"][2]["id"];
        #metadata.append(covertag);
        s = NavigableString("<meta name=\"cover\" content=\"%s\" />" % bookmeta["cover"][2]["id"]);
        metadata.append(s);
    package.append(metadata);
    
    # Manifest is the second.
    manifest = soup.new_tag("manifest");
    for fn, data, name, id, opt in filelist:
        v = {"id": id, "href":fn, "media-type": getMIMEFromFn(fn)}
        # We need to indicate the TOC as the primary nav element.
        if "nav" in opt and opt["nav"]:
            v["properties"] = "nav"; 
        manifest.append(soup.new_tag("item", **v));
    # Add the images too:
    for i, (fn, data, opt) in enumerate(imagelist):
        v = {"href":fn, "media-type": getMIMEFromFn(fn)};    
        # Give it an id
        v["id"] = opt["id"] if "id" in opt else ("image-" + str(i));
        # Set properties:
        if "cover-image" in opt and opt["cover-image"]:
            v["properties"] = "cover-image";

        manifest.append(soup.new_tag("item", **v));
    package.append(manifest);

    # Spine is the third.
    spine = soup.new_tag("spine", toc="ncx");
    for fn, cont, name, id, opt in spinelist:
        # Start each chapter on a right page:
        v = {"idref": id};
        if "linear" in opt and not opt["linear"]:
            v["linear"] = "no";
        spine.append(soup.new_tag("itemref", **v));
    package.append(spine);

        
    return soup.prettify(formatter=None);


def buildNCX(uid, bookmeta, filelist):
    soup = bs4(features='xml');
    ncx = soup.new_tag("ncx", **{"xmlns": "http://www.daisy.org/z3986/2005/ncx/", "version": "2005-1"});
    
    # Set up shorthand to add an element with some contents:
    def soup_tag(a, c):
        rv = soup.new_tag(a);
        rv.append(c);
        return rv;
        
    def meta_tag(n, c):
        rv = soup.new_tag("meta", **{"content": c });
        rv.attrs['name'] = n;
        return rv;

    
    head = soup.new_tag("head");
    head.append(meta_tag("dtb:uid", uid));
    head.append(meta_tag("dtb:depth", "1"));
    head.append(meta_tag("dtb:totalPageCount", "0"));
    head.append(meta_tag("dtb:maxPageNumber", "0"));
    ncx.append(head);

    ncx.append(soup_tag("docTitle", soup_tag("text", bookmeta["title"])));
    ncx.append(soup_tag("docAuthor", soup_tag("text", bookmeta["author"])));
    
    navmap = soup.new_tag("navMap");
    i = 0;
    for fname, data, name, id, opt in filelist:
        v = {"id": "navpoint-" + id};
        if "linear" not in opt or opt["linear"]:
            i += 1;
            v["playOrder"] = str(i);
        navpoint = soup.new_tag('navPoint', **v);
        navpoint.append(soup_tag("navLabel", soup_tag("text", name)));
        navpoint.append(soup.new_tag("content", src=fname));
        navmap.append(navpoint);
    ncx.append(navmap);

    return ncx.prettify();


def epub(inp, fn, styler, args):
    # Split it into metadata, chapters, and images.    
    meta, chpt, imgs = inp;
    # Sort the chapters
    chpt.sort();

    # Prepare the UUID and the creation time:
    uid = str(uuid.uuid5(PUBLISHER_NAMESPACE, fn)); # Generate a file UUID
    modtime = PUBLISHER_TIME();    
    
    # From Chapter Number to filename:
    htmlFn = lambda fn: "html/" + (("p" + str(fn)) if str(fn)[0].isdigit() else str(fn)) + ".xhtml";
    imageFn = lambda fn: "images/" + fn;

    # An in-order list of chapters in the book:
    # As a 5-tuple: Filename, content, Text title, id, additional properties
    chapterList = [(htmlFn(id), ch["content"], ch["name"], "c" + str(id), {}) for (id, ch) in chpt];
    
    # Create a cover page if we need to:
    if "cover" not in meta and not args.no_cover:
        cover = getCover(args.cover);
        print "\tCover: \t" + cover.name + ".";
        meta["cover"] = cover.cover(meta); 
        # Give it a filename and options
        meta["cover"] = ("cover" + meta["cover"][0], meta["cover"][1], {"cover-image":True, "id":"cover-image"});

    if len(imgs) > 0:
        print "\tImages are not supported yet!";  
    
    # The cover and TOC
    cover = (htmlFn("cover"), styler.cover(meta), "Cover", "cover", {"linear": True});
    toc = (htmlFn("toc"), styler.contents(buildTOCInner(chapterList)),  "Table of Contents", "toc", {"linear": False, "nav": True});
    
    spineList = [cover, toc] + chapterList;
    spineList = [(fname, styler.page(meta["title"] + ": " + name, data), name, id, opt) for (fname, data, name, id, opt) in spineList]
    imageList = [];    # TODO: Add every image to imageList;
    if "cover" in meta:
        # We want the absolute filename in the imageList, but not passed to the styler.
        imageList.append((imageFn(meta["cover"][0]), meta["cover"][1], meta["cover"][2]));

    auxList = [("style.css", styler.css(), "Main Stylesheet", "style", {}),
           ("toc.ncx", buildNCX(uid, meta, spineList), "Navigation Control", "ncx", {})];
    fileList = spineList + auxList;
    
    # Write the OPF file:
    opf = buildOPF(uid, modtime, meta, fileList, spineList, imageList);    
    
    try:
        tmpfile = '.temp'
        # Now we write everything to the output file
        epb = initFile(fn);
        epb.writestr(OEBPS + "content.opf", opf);
        
        # Now, we write all the files:
        for fn, data, name, id, opt in fileList:
            epb.writestr(OEBPS + fn, data.encode('utf-8'));
        for fn, data, opt in imageList:
            with open(tmpfile, 'wb') as fsrc:
                fsrc.write(data);

            epb.write(tmpfile, OEBPS + fn);
    finally:
        # Close the file.
        epb.close();
        if (path.exists(tmpfile)):
            remove(tmpfile);
    
    return True;
