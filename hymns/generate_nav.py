#!/usr/bin/env python
# This will generate HTML files to be used for navigation controls 
import sys, os, shutil, pg, re 
from db_functions import *
from file_functions import *

# Output dir parameter (or default)
output_dir = "build/hymn_verse_html"
if (len(sys.argv) >= 2) :
  output_dir = sys.argv[1]

# Create the output directory if necessary
if (not os.path.exists(output_dir)) :
  os.makedirs(output_dir)
  print "Creating directory "+output_dir


# Get the template parameter
templateFile = "nav_template.html"
if (len(sys.argv) >= 3) :
  templateFile = sys.argv[2]

# Load the template
templateHtml = readFile(templateFile)
if (len(templateHtml) < 1):
  print "Error Generating Navigation. No data in template file:"+templateFile
  exit(1)


# Get the file extension parameter
fileExtension = "html"
if (len(sys.argv) >= 4) :
  fileExtension = sys.argv[3]

pagePath = ""
if (fileExtension == "xhtml"):
  pagePath = "../pages/"


def isLeafNode(hnumStr, hnums):
  "Returns true if the hnum specified has no child nodes"
  leaf = True
  for nextNum in range(0,10): #check all children 
    nextHnum = hnumStr+str(nextNum)
    if (int(nextHnum) in hnums) and (int(nextHnum) != 0):
      leaf = False  # if any child is valid this is not a leaf
  return leaf
 


# Go through all the hymns
print "Generating navigation pages in "+output_dir
hnums = dbGetCol("select hnum from hymn order by hnum")

# add a fake hymn 0, used as a nav root
hnums.append(0)

for hnumInt in hnums: 
  hnumStrFile = str(hnumInt).rjust(4,'0') #right justified padded with 0 (for filenames)
  hnumStr = str(hnumInt)   # left justified (for boxes)
  html = templateHtml 

  # Fill the boxes with the number selected
  counter = 0
  if hnumInt != 0 :  # Don't display just a zero
    for numC in hnumStr:  # for each digit in the number
      counter += 1
      html = html.replace("~NUM"+str(counter)+"~", numC)
  while counter < 4 :  # for the rest of the four digits
    counter += 1
    html = html.replace("~NUM"+str(counter)+"~", "")

  # Update the navigation links
  #Go button
  html = html.replace("~NAVgo~", pagePath+hnumStrFile)

  # Check if this page is a leaf node
  if isLeafNode(hnumStr, hnums) :
    # We don't need to generate this page at all, it's never called
    continue

  # For each number button
  for num in range(0,10):
    newHnum = hnumStr+str(num)
    
    # Check if this is a leaf node button (then we go directly to the page)
    isLeaf = isLeafNode(newHnum, hnums)
    
    # Error checking, see if the new hnum is valid
    if not int(newHnum) in hnums:
      newHnum = hnumStr
      # For image buttons
      html = html.replace("button_"+str(num)+".jpg", "button_blank.jpg")
      # For text buttons
      html = html.replace("&#160;"+str(num), "")
    
    newPath = "nav_"+newHnum.rjust(4,'0')    
    if isLeaf:
      newPath = pagePath+newHnum.rjust(4,'0')  # go directly to the page
    # setup the button URL
    html = html.replace("~NAV"+str(num)+"~", newPath)

  #Backspace button
  html = html.replace("~NAVbackspace~", "nav_"+(hnumStr[:-1]).rjust(4,'0'))


  #Special handling for the 0 case
  if hnumInt == 0: 
    #No go button for hymn 0
    html = html.replace('"'+pagePath+'0000.'+fileExtension+'"', '"nav_0000.'+fileExtension+'"')
    html = html.replace("button_go.jpg", "button_go_blank.jpg")
    #0 button doesn't do anything on the 0 page
    html = html.replace("button_0.jpg", "button_blank.jpg")
    #When no numbers display, we need to put something in there to maintain the height
    html = html.replace(">   <", ">&#160;<")

    #Copy the template to index.html as well as nav_0000.html 
    #For ebooks (xhtml) we don't need the index.xhtml page 
    if (fileExtension != "xhtml") :
      writeStringToFile(output_dir+"/index."+fileExtension, html)

  
  # Write out the file
  fileName = output_dir+"/nav_"+hnumStrFile+"."+fileExtension
  writeStringToFile(fileName, html)
  
print "Done generating navigation"


