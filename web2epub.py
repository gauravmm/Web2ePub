"""
Web2Pub.py
Scrapes websites and converts them to ePub, using a pluginnable framework.

GauravManek
"""

import plugins, argparse, urlparse, re;
from scraper import scrape;
from publisher import epub;
from plugins import getStyle;
from os import path;
		
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
	return re.sub("[^0-9a-zA-Z -]", '_', title).strip() + ".epub";

def run(args):
	styler = getStyle(args.style[0]);
	if not styler:
		raise RuntimeError("Cannot find output style " + args.style + ".");
	print "Loaded Style: \t" + styler.name + ".";

	print "Scraping Website";
	web = scrape(args.url, styler, cache=(not args.no_cache));
	
	fout = title_fn(web[0]["author"] + " - " + web[0]["title"]);
	if args.out and len(args.out) > 0 and len(args.out[0]) > 0:
		# If args.out is a directory, then we use our custom filename, otherwise
		# we use the given filename.
		if args.out[0][-1] == "/":
			fout = args.out[0] + fout;
		else:
			fout = args.out[0];

		if not fout.lower().endswith(".epub"):
			fout = fout + ".epub";
	
	if args.no_overwrite and path.exists(fout):
		print "Skipped! \"" + fout + "\" exists.";
	else:
		print "Building ePub";
		epub(web, fout, styler, args);
		
		print "Done! Written output to \"" + fout + "\"";
	

if __name__ == "__main__":
	# Parse incoming arguments:
	parser = argparse.ArgumentParser(description='Converts articles/posts/entries from online sources into an ePub file.');
	parser.add_argument('url', type=arg_url, help='A URL to start from.');
	parser.add_argument('-o', '--out', type=str, metavar="OUTPUT", nargs=1, help='The directory or filename to write to. epub automatically appended if necessary. The target directory must exist.');
	parser.add_argument('-s', '--style', type=str, metavar="STYLE", nargs=1, default=["def"], help='The output style to use.');
	parser.add_argument('-c', '--cover', type=str, metavar="COVER", nargs=1, default="png", help='The cover generator to use, if the parser does not find it.');
	parser.add_argument('--no-cover', action='store_const', default=False, const=True, help='Do not generate a cover page if one does not already exist.');
	parser.add_argument('--no-cache', action='store_const', default=False, const=True, help='Force a cache miss and redownload the source material on this request.');
	parser.add_argument('--no-overwrite', action='store_const', default=False, const=True, help='Skip if the destination file exists.');


	args = parser.parse_args();
	 
	try:
		plugins.load();
		run(args);
	except (RuntimeError, TypeError) as e:
		print "Error: {0}".format(e);
		raise;