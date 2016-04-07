"""
Default SVG cover image generator

@author: GauravManek
"""
import plugins;
from math import floor;
from bs4 import BeautifulSoup as bs4;

class DefaultSVGCover(plugins.BaseCover):
	def __init__(self):
		# A short string used to report this name in the style.
		self.name = "Default SVG Cover";
		# A short string used to identify this styling option in the commandline.
		# Does not have to be different than the Style devstr
		self.devstr = "svg";

	# Produces a (ext, data) tuple, given:
	#   bookmeta = The book metadata.
	#
	# The output is:
	#   ext  = File extension of data, which must be supported by the ePub standard.
	#   data = Image Data.
	def cover(self, bookmeta):
		soup = bs4(features='xml');
		svg = soup.new_tag("svg", width="600", height="800", xmlns="http://www.w3.org/2000/svg");

		# Background:
		svg.append(soup.new_tag("rect", fill="#000", height="802", width="601", y="-1", x="-1"));
		svg.append(soup.new_tag("rect", fill="#FFF", height="780", width="580", y="10", x="10"));
		svg.append(soup.new_tag("rect", fill="#666", height="390", width="580", y="10", x="10"));

		# Title:
		MAX_CHAR_LINE = 40;
		MAX_LINE = 5;
		tt = [""];
		# Word wrapping:
		for word in bookmeta["title"].split():
			line = tt.pop();
			if len(line) == 0 or len(line) + len(word) < MAX_CHAR_LINE:
				tt.append(line + word + " ");
			else:
				tt.append(line);
				tt.append(word + " ");
		# Strip all lines:
		tt = [t.strip() for t in tt];

		offset = (floor(380/36) - len(tt))*20 + 36;
		for l in range(min(len(tt), MAX_CHAR_LINE)):
			ln = soup.new_tag("text", **{
				"text-anchor": "middle",
				"x": "300",
				"y":str(40*l + offset),
				"font-family":"Helvetica, Arial, sans-serif",
				"font-size":"36px",
				"stroke-width":"0",
				"fill":"#FFF"
			});
			ln.append(tt[l]);
			svg.append(ln);

		# Center Polygon
		poly = soup.new_tag("svg", **{"x": "250", "y": "350"});
		poly.append(soup.new_tag("polygon", **{
			"stroke-width": "5",
			"stroke": "#FFF",
			"fill": "#CCC",
			"points": "74,91.57 26,91.57 2,50 26,8.43 74,8.43 98,50 74,91.57"
		}));
		svg.append(poly);

		# Author
		ln = soup.new_tag("text", **{
				"text-anchor": "middle",
				"x": "300",
				"y": "500",
				"font-family":"Helvetica, Arial, sans-serif",
				"font-style":"italic",
				"font-size":"32px",
				"stroke-width":"0",
				"fill":"#000"
			});
		ln.append(bookmeta["author"]);
		svg.append(ln);

		# Attrib
		if "attrib" in bookmeta:
			ln = soup.new_tag("text", **{
					"text-anchor": "middle",
					"x": "300",
					"y": "780",
					"font-family":"Helvetica, Arial, sans-serif",
					"font-size":"24px",
					"stroke-width":"0",
					"fill":"#999"
				});
			ln.append(bookmeta["attrib"]);
			svg.append(ln);

		svg = svg.prettify();
		svg = svg.encode("UTF-8");
		return (".svg", svg);

if __name__ == "plugins":
	plugins.register(DefaultSVGCover());        
