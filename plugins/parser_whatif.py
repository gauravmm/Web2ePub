import plugins;
from bs4 import BeautifulSoup as bs4c;
from bs4 import NavigableString, Tag;

escapeHTML = (EntitySubstitution()).substitute_xml;      
				 
class WhatIfXKCDParser(plugins.BaseWebsiteParser):
	def __init__(self):
		self.name = "XKCD What-If";
		pass;
		
	def canParse(self, url):
		return url.netloc == "what-if.xkcd.com";
	
	def getSimplePageId(self, pid):
		return pid;
		
	def getIdFromUrl(self, url):
		m = re.match("/(\d+)/", url.path);
		if m:
			return int(m.group(1));
		else:
			return 1;

	def getUrlFromId(self, pid):
		return "http://what-if.xkcd.com/%d/" % pid;
	
	def parsePage(self, source, pid, image_prefix, styler):
		
		rv = {};
		rv["name"] = "Unknown"
		rv["title"] = "What If"
		rv["author"] = "Randall Munroe";
		rv["cover"] = ("cover.png", "http://what-if.xkcd.com/imgs/whatif-logo.png");

		rv["id"] = pid;
		rv["images"] = [];

		rv["also"] = [pid + 1];

		soup = bs4c(source, "lxml");

		if soup.find('title') and "404 - Not Found" in soup.find('title').stripped_strings:
			return None;

		rv["data"] = u"";

		article = soup.find("article", class_="entry");
		if not article:
			return None;

		footnote_count = 0;
		footnotes = [];
		for i,child in enumerate(c for c in article.children if not isinstance(c, NavigableString) or unicode(c).strip() != ""):
			if i == 0 and child.name == "a":
				h = child.get_text("", strip = True);
				rv["data"] += styler.header(1, h) + u"\n";
				rv["name"] = h;
			elif type(child) == Tag and child.has_attr('id') and child["id"] == "question":
				if not i == 1:
					rv["data"] += styler.section_break();
				rv["data"] += u"<p>" + child.get_text("", strip = True) + "</p>\n";
			elif type(child) == Tag and child.has_attr('id') and child["id"] == "attribute":
				rv["data"] += u"<p>" + child.get_text("", strip = True) + "</p>\n";
				rv["data"] += styler.section_break();
			else:
				# Continue processing the line, adding images to the images array.
				if type(child) == Tag and child.name == "img":
					path = child["src"];
					path_parts = path.split("/");
					img_src = "http://what-if.xkcd.com" + path;
					img_dst = path_parts[-1];
					rv["data"] += u"<img src=\"" + image_prefix + img_dst + "\" title=\"" + child["title"] + "\" />\n";
					rv["images"].append((img_dst, img_src));
				elif type(child) == Tag and child.name in ["p", "div"]:
					s = [];
					for t in child.children:
						# Handle footnotes.
						if type(t) == Tag and t.name == "span" and t.has_attr("class") and "ref" in t["class"]:
							fn_id = "#fn" + str(footnote_count);
							ref = t.find("span", class_="refnum");
							txt = t.find("span", class_="refbody");
							s.append("<sup><a epub:type=\"noteref\" href=\"" + fn_id + "\">" + unicode(ref.contents[0]) + "</a></sup>");

							txt.name = "aside";
							del txt["class"];
							del txt["style"];
							txt["epub:type"] = "footnote";
							txt["id"] = fn_id;

							footnotes.append(unicode(txt));
							footnote_count += 1;
						elif type(t) == Tag and t.name == "img":
							path = t["src"];
							path_parts = path.split("/");
							img_src = path;
							img_dst = path_parts[-1];
							s.append(u"<img src=\"" + image_prefix + img_dst + "\" title=\"" + t["title"] + "\" />\n");
							rv["images"].append((img_dst, img_src));
						else:
							s.append(unicode(t));

					opentag = u"<p>";
					if child.name == "div":
						opentag = "<p style=\"border: thin solid black; \">";

					rv["data"] += opentag + u"".join(s) + "</p>\n";


		rv["data"] += "\n".join(footnotes);
		
		return rv;
		
if __name__ == "plugins":
	plugins.register(WhatIfXKCDParser());