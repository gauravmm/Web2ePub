"""
Style for the Nook GlowLight Plus.

@author: GauravManek
"""
from plugins import register;
from style_default import DefaultStyle;

class NookGPStyle(DefaultStyle):
	def __init__(self):
		self.name = "Nook GlowLight Plus";
		self.devstr = "ngp";

	def css(self):
		rv = super(NookGPStyle, self).css();
		return rv + u"""
div.sec_brk { width:100%; text-align:center; padding:0.5em; background:white; }
body { padding: 0; margin: 0; }
img { max-width: 100%; margin: auto; }""";

	# Produce a string containing the markup for a section break:
	def section_break(self):
		return u"<div class=\"sec_brk\">\u2014\u3000\u00A7\u3000\u2014</div>";

	def edit_book_metadata(self, bookmeta):
		# Lastname, Firstname required by NGP:
		if "attrib" in bookmeta:
			bookmeta["author"] = bookmeta["attrib"] + ", " + bookmeta["author"];
		return bookmeta;


if __name__ == "plugins":
	register(NookGPStyle());        
