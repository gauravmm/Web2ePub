import argparse, urlparse, re;
from scraper import scrape;
from publisher import epub;
        
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
    return re.sub("[^0-9a-zA-Z]", '_', title) + ".epub";

def run(args):
    web = scrape(args.url);
    
    fout = None;
    if args.out:
        fout = args.out[0];
        if not fout.lower().endswith(".epub"):
            fout = fout + ".epub";
    else:
        fout = title_fn(web[0]["title"]);

    print fout;

if __name__ == "__main__":
    # Parse incoming arguments:
    parser = argparse.ArgumentParser(description='Converts articles/posts/entries from online sources into an ePub file.');
    parser.add_argument('url', type=arg_url, help='A URL to start from.');
    parser.add_argument('-o', '--out', type=str, metavar="OUTPUT", nargs=1, help='The filename to write to. epub automatically appended if necessary.');

    # args = parser.parse_args();
    args = parser.parse_args(["http://m.fanfiction.net/s/5483280/1/Harry-Potter-and-the-Champion-s-Champion"]);
   
    try:
        run(args);
        
    except (RuntimeError, TypeError) as e:
        print "Error: {0}".format(e);
        raise;