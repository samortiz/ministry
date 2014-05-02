#!/usr/bin/env python
# This will generate ixl file used to create the pdb
import sys, os, shutil, pg, re, datetime
from db_functions import *
from file_functions import *

# Setup
templateFile = "hymn_verse_ixl_template"
outputFile = "hymn_verse.ixl"
rootPath = "/home/sortiz/project/ministry/hymn_verse"


# Output dir parameter (or default)
output_dir = "build/hymn_verse_html"
if (len(sys.argv) >= 2) :
  output_dir = sys.argv[1]

# Create the output directory if necessary
if (not os.path.exists(output_dir)) :
  os.makedirs(output_dir)
  print "Creating directory "+output_dir

# Get the pdbFilename from a parameter
pdbFilename = "hymn_verse.pdb"
if (len(sys.argv) >= 3) :
  pdbFilename = sys.argv[2]

# Get the verses parameter
withVerses = True
if (len(sys.argv) >= 4) :
    withVerses = (sys.argv[3] != "noverses")


# Load the template
template = readFile(templateFile)

# Calculate the outputpath
outputPath = rootPath+"/"+output_dir

# Get all the files to include in this pdb
# Start with the indexes
paths    = "<Path>"+outputPath+"/index.html</Path>\n"
navPaths = "<Path>"+outputPath+"/nav_0000.html</Path>\n"

# Go through all the hymns
hnums = dbGetCol("select hnum from hymn order by hnum")
for hnumInt in hnums: 
  hnum = str(hnumInt).rjust(4,'0') #right justified padded with 0 (for filenames)
  paths += "<Path>"+outputPath+"/"+hnum+".html</Path>\n"
  navPaths += "<Path>"+outputPath+"/nav_"+hnum+".html</Path>\n"

# Calculate the version
today = datetime.date.today()
version = today.strftime('%b %d %Y')

# Calculate the Title
title = "Hymns with Verses"
if (not withVerses):
  title = "Hymns and Songbook"

# Construct the file contents
template = template.replace("~TITLE~", title).replace("~VERSION~",version)
template = template.replace("~PDB_PATH~",outputPath+"/"+pdbFilename)
template = template.replace("~PATHS~", paths+navPaths)

# Write out the file
fileName = output_dir+"/"+outputFile
writeStringToFile(fileName, template)
  
print "Finished generating "+fileName


