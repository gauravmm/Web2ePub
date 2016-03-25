import argparse, urlparse;
from scraper import scrape;
        
def arg_url(string):
    if not string[0:7] == "http://" and not string[0:8] == "https://":
        string = "http://" + string;
        
    parse = urlparse.urlparse(string, scheme='http', allow_fragments=False);
    if parse[1] == "" or parse[2]=="":
        raise argparse.ArgumentTypeError("\"%r\" is not a valid url" % string)
    return parse;

def run(args):
    web = scrape(args.url);
    

if __name__ == "__main__":
    # Parse incoming arguments:
    parser = argparse.ArgumentParser(description='Converts articles/posts/entries from online sources into an ePub file.');
    parser.add_argument('url', type=arg_url, help='A URL to start from.')
    # args = parser.parse_args();
    args = parser.parse_args(["http://m.fanfiction.net/s/5483280/1/Harry-Potter-and-the-Champion-s-Champion"]);
    
    try:
        run(args);
    except (RuntimeError, TypeError) as e:
        print "Error: {0}".format(e);
        raise;