#! /usr/bin/env python
# functions for dealing with books and book html
import os, time, shutil

# ---------------------- Misc Functions --------------------------------
def readFile(fileName):
  return open(fileName, 'r').read()

# Ensures that a directory exists, it creates it if necessary
def ensure_dir(dir):
  if not os.path.exists(dir):
    os.makedirs(dir)

# Creates a file and writes the string into it
def writeStringToFile(fileName, contentStr):
  file = open(fileName,"w")
  file.write(contentStr)
  # File closing is handled automaticaly (so the docs say!)
  file.close() # But I'm not entirely sure about that... :) 




# -----------------------------------------------------------------------

# Clean up file names
def cleanFileName(rawFileName):
  cleanFileName = ""
  
  # Loop through and copy each character (except funny ones)
  for char in rawFileName :
    cnum = ord(char)
    if cnum == 32 or cnum == 45: # space or hyphen
      cleanFileName += "_"  
    elif cnum >= 48 and cnum <= 57 : # digit 0-9
      cleanFileName += char
    elif ((cnum >= 65 and cnum <= 90) # uppercase
          or (cnum >= 97 and cnum <= 122)) : # lowercase
      cleanFileName += char
      
  return cleanFileName
  

# Clean up various problems in the HTML
def cleanupHtml(rawHtml):
  # Convert funny quotes to HTML entities
  html = rawHtml.replace('\xe2\x80\x9c', '&#8220;')  # Left double quote
  html = html.replace('\xe2\x80\x9d', '&#8221;')  # Right double quote
  html = html.replace('\xe2\x80\xa6', '...')  # ellipsis
  html = html.replace('\xe2\x80\x98', '&#8216;')  # left single quote
  html = html.replace('\xe2\x80\x99', '&#8217;')  # Right single quote
  html = html.replace('\xe2\x80\x94', '-') # some kind of hyphen
  html = html.replace('\xe2\x80\x93', '-') # some kind of hyphen
  html = html.replace('\xc3\xbc', 'u')  # u with double dots above it
  html = html.replace('\xe2\x80\xa2', '-') # Funny centered dot (bullet)
  html = html.replace('\xc3\xa0', '&#224;') # a with accent
  html = html.replace('\xc3\xa9', '&#233;') # e with an up accent
  html = html.replace('\xc3\xa8', '&#232;') # e with a down accent
  html = html.replace('\xc3\xa7', '&#231;') # c with a hook under it
  html = html.replace('\xc2\xa0', ' ') # maybe whitespace?
  html = html.replace('\xc2\xbc', ' ') # weird fraction
  html = html.replace('\xc2\xbd', ' ') # weird fraction
  html = html.replace('\xc2\xbe', ' ') # weird fraction
  html = html.replace('\xc2\xad', ' ') # whitespace maybe?
 
  # Go through all the characters, see if there are any error-characters
  count = 0
  for char in html:
    if ord(char) > 127:
      print "Found Invalid Char at "+str(count-113)
      print "Hex : %2x %2x %2x " % (ord(char), ord(html[count+1]), ord(html[count+2]) )
      print "Context : "+html[count-10:count+10]
      os._exit(1)
    count += 1
  
  return html
  
# Create a nice looking display name for the book Title
def bookDisplayName(rawBookName):
  bookTitle = cleanupHtml(rawBookName)
  if bookTitle.endswith(", The"):
    bookTitle = "The "+bookTitle[:len(bookTitle)-5]
  if bookTitle.endswith(", A"):
    bookTitle = "A "+bookTitle[:len(bookTitle)-3]
  if bookTitle.endswith(", An"):
    bookTitle = "An "+bookTitle[:len(bookTitle)-4]
  return bookTitle
  



