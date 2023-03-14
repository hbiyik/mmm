'''
Created on Nov 4, 2022

@author: boogie
'''
import sys
import re
from PyPDF2 import PdfReader

reader = PdfReader(sys.argv[1])
texts = []
for page in reader.pages:
    texts.extend(page.extract_text().split("\n"))

search_dev = True
found_dev = False
search_reg = False
search_offset = False
search_map = False
search_desc = False
desc = ""

global PREVREG
global OUTFILE

OUTFILE = "from libmmm.model import Device, Reg32, Datapoint\n"

def strip(txt):
    return txt.replace(" ", "").replace(".", "").replace("-", "_")

        
def add_device(match):
    global OUTFILE
    devname = strip(match.group(1))
    devaddr = strip(match.group(2))
    OUTFILE += "\n\nclass %s(Device):\n    def __init__(self, start=%s):\n" % (devname, devaddr)
    OUTFILE += '        super(%s, self).__init__("%s" , start)\n' % (devname, devname)

def add_register(match):
    global PREVREG
    global OUTFILE
    PREVREG = strip(match.group(2))
    regaddr = strip(match.group(1))
    OUTFILE += '        %s = Reg32("%s", %s)\n' % (PREVREG, PREVREG, regaddr)
    OUTFILE += '        self.block(%s)\n' % (PREVREG)

def add_datapoint(match):
    global PREVREG
    global OUTFILE
    if ":" in match.group(1):
        end, start = strip(match.group(1)).split(":")
        if start == "":
            start = int(end)
            size = 1
        else:
            vals = [int(end), int(start)]
            start = min(vals)
            end = max(vals)
            size = end - start + 1
    else:
        size = 1
        start = int(strip(match.group(1)))
    
    default = strip(match.group(3))
    if default in ["x", "", "/"]:
        default = None
    else:
        default = int(default, 16)
    dataname = strip(match.group(4))
    OUTFILE += '        %s.register(%s, %s, Datapoint("%s", default=%s))\n' % (PREVREG, start, size, dataname, default)


def printmatches(match):
    print([match.group(x + 1).replace(" ", "").replace(".", "") for x in range(match.lastindex)])
 
for text in texts:
    if search_dev and text.replace(" ", "") == "ModuleNameBaseAddress":
        search_dev = False
        found_dev = True
    elif found_dev:
        match = re.search("(.+?)\s([0-9A-Fa-fx\s]+)", text)
        printmatches(match)
        add_device(match)
        found_dev = False
        search_reg = True
    elif search_reg:
        match = re.search("[Ofset\sAdrs]+:\s?(0\s?[xX][0-9a-fA-F\s]+?)[RegistrNam\s]+:\s?(.+)", text)
        if match:
            printmatches(match)
            add_register(match)
            search_reg = False
            search_dev = False
            search_offset = True
    if search_offset:
        match = re.search("([0-9\:]+?)\s*?([RO\/W]+?)\s+([x0-9a-fA-F\s]+?|\/)\s([a-zA-Z_0-9\s]+)", text)
        if match:
            printmatches(match)
            add_datapoint(match)
            # search_offset = False
            search_reg = False
            search_map = True
    if search_map:
        match = re.search("(.+?): (.+)", text)
        if match:
            printmatches(match)
        else:
            search_map = False
            search_offset = True
            search_reg = True
            search_dev = True
            
with open("out.py", "w") as f:
    f.write(OUTFILE)
