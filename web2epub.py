"""
Web2Pub.py
Scrapes websites and converts them to ePub, using a pluginnable framework.

GauravManek
"""

import plugins, argparse, urlparse, re;
from scraper import scrape;
from publisher import epub;
from plugins import getStyle;
        
def arg_url(string):
    if not string[0:7] == "http://" and not string[0:8] == "https://":
        string = "http://" + string;
        
    parse = urlparse.urlparse(string, scheme='http', allow_fragments=False);
    if parse[1] == "" or parse[2]=="":
        raise argparse.ArgumentTypeError("\"%r\" is not a valid url" % string)
    return parse;

def title_fn(title):
    # Convert to ASCII:
    title = title.encode('ascii', 'ignore');
    # Remove ' within words:
    title = re.sub("[\b'\b]", '', title);    
    return re.sub("[^0-9a-zA-Z ]", '_', title).strip() + ".epub";

def run(args):
    styler = getStyle(args.style[0]);
    if not styler:
        raise RuntimeError("Cannot find output style " + args.style + ".");
    print "Loaded Style: \t" + styler.name + ".";

    print "Scraping Website";
    web = scrape(args.url, styler);
    
    fout = None;
    if args.out:
        fout = args.out[0];
        if not fout.lower().endswith(".epub"):
            fout = fout + ".epub";
    else:
        fout = title_fn(web[0]["title"]);

    
    print "Building ePub";
    epub(web, fout, styler, args);
    
    print "Done! Written output to \"" + fout + "\"";
    

if __name__ == "__main__":
    # Parse incoming arguments:
    parser = argparse.ArgumentParser(description='Converts articles/posts/entries from online sources into an ePub file.');
    parser.add_argument('url', type=arg_url, help='A URL to start from.');
    parser.add_argument('-o', '--out', type=str, metavar="OUTPUT", nargs=1, help='The filename to write to. epub automatically appended if necessary.');
    parser.add_argument('-s', '--style', type=str, metavar="STYLE", nargs=1, default=["def"], help='The output style to use.');
    parser.add_argument('-c', '--cover', type=str, metavar="COVER", nargs=1, default="png", help='The cover generator to use, if the parser does not find it.');
    parser.add_argument('--no-cover', action='store_const', default=False, const=True, help='Do not generate a cover page if one does not already exist.');

    # args = parser.parse_args();
    args = parser.parse_args(["http://m.fanfiction.net/s/5483280/1/Harry-Potter-and-the-Champion-s-Champion", "-s",  "ngp"]);
   
    try:
        plugins.load();
        run(args);
    except (RuntimeError, TypeError) as e:
        print "Error: {0}".format(e);
        raise;