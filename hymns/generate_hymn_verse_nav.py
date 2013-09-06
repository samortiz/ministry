#!/usr/bin/env python
# This will generate HTML files to be used for navigation controls 
import os, shutil, pg, re 
from db_functions import *
from file_functions import *

# Setup 
templateHtml = readFile("generate_hymn_verse_nav_template.html")
dir = "hymn_verse_html"


# Create the root directory
if (not os.path.exists(dir)) : 
  os.makedirs(dir)

# Go through all the hymns
hnums = dbGetCol("select hnum from hymn order by hnum")

# add a fake hymn 0, used as a root
hnums.append(0)

for hnumInt in hnums: 
  hnumStrFile = str(hnumInt).rjust(4,'0') #right justified padded with 0 (for filenames)
  hnumStr = str(hnumInt)   # left justified (for boxes)
  print "Processing "+hnumStr
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
  html = html.replace("~NAVgo~", hnumStrFile)

  #Number buttons
  for num in range(0,10):
    newHnum = hnumStr+str(num)
    # Error checking, see if the new hnum is valid
    if not int(newHnum) in hnums:
      newHnum = hnumStr
      html = html.replace("button_"+str(num)+".jpg", "button_blank.jpg")
    newPath = "nav_"+newHnum.rjust(4,'0')
    
    # Check if this is a leaf node number (go directly to the page)
    isLeafNode = True
    for nextNum in range(0,10): #check all children 
      nextHnum = newHnum+str(nextNum)
      if int(nextHnum) in hnums:  
        isLeafNode = False  # if any child is valid this is not a leaf
    if isLeafNode:
      newPath = newHnum.rjust(4,'0')  # go directly to the page
    # setup the button URL
    html = html.replace("~NAV"+str(num)+"~", newPath)

  #Backspace button
  html = html.replace("~NAVbackspace~", "nav_"+(hnumStr[:-1]).rjust(4,'0'))


  #Special handling for the 0 case
  if hnumInt == 0: 
    #No go button for hymn 0
    html = html.replace('"0000.html"', '"nav_0000.html"')
    html = html.replace("button_go.jpg", "button_go_blank.jpg")
    # 0 button doesn't do anything on the 0 page
    html = html.replace("button_0.jpg", "button_blank.jpg")


    #Copy the template to index.html as well as nav_0000.html 
    writeStringToFile(dir+"/index.html", html)

  
  # Write out the file
  fileName = dir+"/nav_"+hnumStrFile+".html"
  writeStringToFile(fileName, html)
  
print "Done generating navigation"


