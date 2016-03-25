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

if __name__ == "plugins":
	register(NookGPStyle());        
