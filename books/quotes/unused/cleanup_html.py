#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Cleans up the html in preparation for the mead engine
import os, re, sys


# Path Variables
dataDir = 'mead/data'

abbrs = ['Gen', 'Exo', 'Lev', 'Num', 'Deut', 'Josh', 'Jud', 'Ruth', '1 Sam', '2 Sam', 
         '1 Ki', '2 Ki', '1 Chron', '2 Chron', 'Ezra', 'Neh', 'Esther', 'Job', 
         'Psa', 'Prov', 'Ecc', 'SS', 'Isa', 'Jer', 'Lam', 'Ezk', 'Dan', 'Hos', 'Joel', 
         'Amo', 'Oba', 'Jon', 'Mic', 'Nah', 'Hab', 'Zeph', 'Hag', 'Zech', 'Mal', 
         'Matt', 'Rom', '1 Cor', '2 Cor', 'Gal', 'Eph', 'Phil', 'Col', '1 Thes', '2 Thes', 
         '1 Tim', '2 Tim', 'Tit', 'Phil', 'Heb', 'Jam', '1 Pet', '2 Pet', 'Rev']

# Get book from the parameter
book = ""
if (len(sys.argv) >= 2) :
  book = sys.argv[1]
else :
  exit(1)

pages = os.listdir(dataDir+"/"+book)

# Go through each page
for page in pages :
  pageFile = dataDir+"/"+book+"/"+page
  html = open(pageFile, "r").read()

  # Replace quotes
  html = html.replace('”', '"').replace('“', '"').replace('’', "'")

  # Fix book abbreviations (period ends the sentence)
  for abbr in abbrs :
    html = html.replace(abbr+".", abbr)
    
  open(pageFile, "w").write(html)



