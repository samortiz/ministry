# Get books from the web

import urllib, urllib2, cookielib, sgmllib
import os, random, time


#File Variables
rawHtmlDir = 'raw_html'
cleanHtmlDir = 'clean_html'

# ---------------------- Misc Functions --------------------------------

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


#Cuts a string from the first startStr to the first endStr and returns it
# Note: this also strips off whitespace from the final string
def cutStr(sourceStr, startStr, endStr):
  startCutIndex = sourceStr.find(startStr) + len(startStr)
  endCutIndex = sourceStr.find(endStr)
  return sourceStr[startCutIndex:endCutIndex].strip()


# Removes all the header/footer stuff from the HTML page
# Note: This is very sensitive to changes on the server and may need to be changed when there are updates
def cleanupHtml(pageHtml):
  cleanHtml = pageHtml

  #Cut off the header
  startPos = cleanHtml.find('<div id="ministry-text">')
  if (startPos >= 0):
    cleanHtml = cleanHtml[startPos+25:] #+25 to remove the found text

  #Cut off the footer
  endPos = cleanHtml.find('<div class="row tools">')
  if (endPos > 0):
    cleanHtml = cleanHtml[:endPos-28] # -28 to trim off the '</div> <hr>'

  cleanHtml = cleanHtml.strip()
  return cleanHtml


#Returns a list of all the books that have raw_html downloaded but no clean_html generated yet. 
def getMissingBooks():
  missingBooks = []
  #Directory containing all the books downloaded so far
  rawBooks = os.listdir(rawHtmlDir)
  for book in rawBooks:
    if not os.path.exists(os.path.join(cleanHtmlDir, book, "page_001.html")):
      missingBooks.append(book)
  #Return a list of all missing books
  return missingBooks


#----------------------------------------------------------------------------------------------
# Start the main program

#Ensure the clean dir exists
ensure_dir(cleanHtmlDir)

#Get the list of books we need to clean
missingBooks = getMissingBooks()

print 'missing '+ str(len(missingBooks))
print missingBooks

#missingBooks = ['Changing Death into Life'] #DEBUG -force the book
for book in missingBooks:
  print "Cleaning "+book
  ensure_dir(os.path.join(cleanHtmlDir, book))
  for page in os.listdir(os.path.join(rawHtmlDir, book)):
    if (page.find('page_') == 0): # Only process page files  
      pageHtml = open(os.path.join(rawHtmlDir, book, page), 'r').read()
      cleanPageHtml = cleanupHtml(pageHtml);
      writeStringToFile(os.path.join(cleanHtmlDir, book, page), cleanPageHtml)      

