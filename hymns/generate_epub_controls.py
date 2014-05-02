#!/usr/bin/env python
# This will generate HTML files to be used for navigation controls 
import sys, os, shutil, pg, re 
from db_functions import *
from file_functions import *

outputFileName="content.opf"

# Output dir parameter (or default)
output_dir = "build/hymn_verse_html"
if (len(sys.argv) >= 2) :
  output_dir = sys.argv[1]

# Create the output directory if necessary
if (not os.path.exists(output_dir)) :
  os.makedirs(output_dir)
  print "Creating directory "+output_dir


# Get the template parameter
templateFile = ""
if (len(sys.argv) >= 3) :
  templateFile = sys.argv[2]

# Load the template
templateHtml = readFile(templateFile)
if (len(templateHtml) < 1):
  print "Error Generating Navigation. No data in template file:"+templateFile
  exit(1)

manifestHtml = ""
spineHtml = ""


#Go through all the image files in the output directory
for f in sorted(os.listdir(output_dir+"/images")):
  fId, fileExt = os.path.splitext(f)
  mimeType = "image/jpeg"
  if (fileExt == ".gif"):
    mimeType = "image/gif"
  manifestHtml += '<item href="images/'+f+'" id="'+fId+'" media-type="'+mimeType+'"/>\n'


#Go through all the nav files in the output directory
for f in sorted(os.listdir(output_dir+"/nav")):
  fId = os.path.splitext(f)[0]
  manifestHtml += '<item href="nav/'+f+'" id="'+fId+'" media-type="application/xhtml+xml"/>\n'
  spineHtml += '<itemref idref="'+fId+'" />\n'

#Go through all the pages
for f in sorted(os.listdir(output_dir+"/pages")):
  fId = os.path.splitext(f)[0]
  manifestHtml += '<item href="pages/'+f+'" id="page'+fId+'" media-type="application/xhtml+xml"/>\n'
  spineHtml += '<itemref idref="page'+fId+'" />\n'


#Generate the final string
templateHtml = templateHtml.replace("~MANIFEST_FILES~", manifestHtml)
templateHtml = templateHtml.replace("~SPINE_FILES~", spineHtml)

# Write out the file
fileName = output_dir+"/"+outputFileName
writeStringToFile(fileName, templateHtml)
  
print "Done generating "+fileName


