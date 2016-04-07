"""
Default SVG cover image generator

@author: GauravManek
"""
import plugins, io;
from PIL import Image, ImageDraw, ImageFont;
from math import floor;

class DefaultPNGCover(plugins.BaseCover):
	def __init__(self):
		# A short string used to report this name in the style.
		self.name = "Default PNG Cover";
		# A short string used to identify this styling option in the commandline.
		# Does not have to be different than the Style devstr
		self.devstr = "png";

	# Produces a (ext, data) tuple, given:
	#   bookmeta = The book metadata.
	#
	# The output is:
	#   ext  = File extension of data, which must be supported by the ePub standard.
	#   data = Image Data.
	def cover(self, bookmeta):
		im = Image.new("L", (600, 1000), 0);
		draw = ImageDraw.Draw(im)
		
		# Background:
		draw.rectangle((10, 10, 590, 990), 0xFF);
		draw.rectangle((20, 20, 580, 700), 0x33);
		
		# Title:
		MAX_CHAR_LINE = 16;
		MAX_LINE = 5;
		tt = [""];

		# Word wrapping:
		title = bookmeta["title"];
		title = title.replace("and the", "and_the").replace("of the", "of_the");
		for word in title.split():
			line = tt.pop();
			if "_" in word:
				if len(line) > 0:
					tt.append(line);
				tt.append(word.replace("_", " "));
				tt.append("");
			elif len(line) == 0 or len(line) + len(word) < MAX_CHAR_LINE:
				tt.append(line + word + " ");
			else:
				tt.append(line);
				tt.append(word + " ");
		# Strip all lines:
		tt = [t.strip() for t in tt];

		offset = (floor(580/60) - len(tt))*20;
		f36 = ImageFont.truetype("verdana.ttf", 56) 
		for l in range(min(len(tt), MAX_CHAR_LINE)):
			sz = f36.getsize(tt[l]);
			draw.text(((600 - sz[0])/2, 60*l + offset), tt[l], fill=0xFF, font=f36);
			
		poly = [(74,91.57), (26,91.57), (2,50), (26,8.43), (74,8.43), (98,50), (74,91.57)];
		poly = [(x-50, y-50) for x, y in poly];
		draw.polygon([(300 + x*1.1, 700 + y*1.1) for x, y in poly], fill=0xFF);
		draw.polygon([(300 + x, 700 + y) for x, y in poly], fill=0x99);


		f20i = ImageFont.truetype("verdanai.ttf", 40);
		sz = f20i.getsize(bookmeta["author"]);
		draw.text(((600-sz[0])/2, 750), bookmeta["author"], fill=0x00, font=f20i);

		# Attrib
		if "attrib" in bookmeta:
			f24 = ImageFont.truetype("verdana.ttf", 40);
			sz = f24.getsize(bookmeta["attrib"]);
			draw.text(((600-sz[0])/2, 1000 - 15 - sz[1]), bookmeta["attrib"], fill=0x99, font=f24);

		b = io.BytesIO();
		im.save(b, "PNG");
		return (".png", b.getvalue());

if __name__ == "plugins":
	plugins.register(DefaultPNGCover());        
