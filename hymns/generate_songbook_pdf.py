from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import simpleSplit
from db_functions import *
import os

# Bugs and Future Features
# handle non-data lines (comments, refs)
# try smaller fonts for songs that are close to one page
# automatic line breaking (where and how)
# indents (maybe, I'm not sure I like them)
# Funny formatted songs (side by side like 1926, 1722)

#Generated Files 
fileName = 'songbook.pdf' # Final file produced
tempFileName = 'songbook_temp.pdf' # temp, used to test song sizes

#Display Control Settings
renumber = True  # if false use hnum from the db, else renumber starting with 1 and incrementing by 1

# Page Control Settings
# Important! If you are printing booklet style, landscape with two pdf pages per printed page
# Then you need to ensure that the total document has (a multiple of 4)-1 for the page count (-1 because the last page should be blank)
# So you may need to add up to three blank pages, depending how you want it to layout 
insertBlankPageAfterTitlePage = True # if True inserts a blank page after the title page (also effects the leftPage calculation)
insertBlankPageBeforeIndex = False # If True inserts a blank page before the index of first lines and choruses
insertSecondBlankPageBeforeIndex = False # Inserts another blank page before the index

# Display Variables
fontName = 'Helvetica'
fontSize = 18
fontLeading = 20
hymnHeaderFontName = "Helvetica-Bold" # hymn numbers
hymnHeaderFontSize = 24
hymnHeaderFontLeading = 26
pageCountFontName = "Helvetica"
pageCountFontSize = 12
pageCountFontLeading = 14
titleFontName = "Helvetica-Bold" # Page Titles (Index...)
titleFontSize = 24
titleFontLeading = 26

topMargin = 40
leftMargin = 40
rightMargin = 40
bottomMargin = 40
chorusIndent = 20  # distance chorus is indented
stanzaNumIndent = fontSize + 4 # How far left to put the stanza number
stanzaYGap = 10 # Gap between stanzas
hymnHeaderYSpaceBelow = 10
ySpaceBetweenHymns = 20
pageWidth, pageHeight = letter
maxLineWidth = pageWidth - (leftMargin + rightMargin)
maxPageHeight = pageHeight - (topMargin + bottomMargin)
yTopOfPage = pageHeight - topMargin
yBottomOfPage = bottomMargin


# Setup the temp document (for temp drawing), the final canvas will re-assign this later
canvas = Canvas(tempFileName, pagesize=letter)
pageCount = 1  # Global, used to keep track of which page we're on 




def drawHymnLine(x, y, text, hnum):
  canvas.setFont(fontName, fontSize)
  lineWidth = canvas.stringWidth(text, fontName, fontSize) 
  if (lineWidth > maxLineWidth):
    raise Exception("The line of text is too long to fit on the page! hnum="+str(hnum), text)
  canvas.drawString(x,y,text)

  # Split long lines of text (Maybe we should throw an error instead?)
  #textLines = simpleSplit(text, canvas._fontname, canvas._fontsize, maxLineWidth)
  #for splitLine in textLines:
  #  canvas.drawString(x,y,splitLine)
  #  y -= canvas._leading


# Make a new page
def newPage():
  global pageCount
  printFooter()
  canvas.showPage()
  pageCount += 1 

def newPageY(y):
  if (y != yTopOfPage):
    newPage()
  return yTopOfPage

def printFooter():
  canvas.setFont(pageCountFontName, pageCountFontSize)
  canvas.drawCentredString(pageWidth/2, yBottomOfPage-pageCountFontSize, str(pageCount))


# Empty class definition, used as a struct to hold hymn data
class Hymn: pass
class Stanza: pass
class Line: pass
hymnIndex = [] # List of (hnum, lineData)

def loadHymnData(hnum):
  hymn = Hymn()
  hymn.hnum = hnum
  hymn.stanzas = []  # list of Stanza  
  hymn.maxLineWidth = 0 # width of the longest line with the current font settings 
  hymn.twoDigitStanza = False  # True if any stanza has two digits or more

  currStanza = Stanza()
  currStanza.stanza = "" # Unknown first stanza
  currStanza.lines = [] # List of Line

  sql = "select stanza, line, data, type, indent from hymn_line_mod where hnum="+str(hnum)+" order by lineorder"
  hymnLines = db.query(sql).getresult()
  for hymnLine in hymnLines :
    stanza = toString(hymnLine[0])
    line = hymnLine[1]
    data  = toString(hymnLine[2])
    dataType = toString(hymnLine[3])
    indent = hymnLine[4]
    
    if ((currStanza.stanza != stanza) or (line == "1")) : # We are switching to a new stanza
      if (currStanza.stanza != ""): hymn.stanzas.append(currStanza) # add the prev stanza to the list
      # Start a new stanza
      currStanza = Stanza()
      currStanza.stanza = stanza
      currStanza.lines = []
      if currStanza.stanza.startswith('c'):
        currStanza.isChorus = True
      else: 
        currStanza.isChorus = False
      if len(currStanza.stanza) > 1: 
        hymn.twoDigitStanza = True
    
    # Add this hymn line
    currLine = Line()
    currLine.data = data
    currLine.indent = indent
    currLine.dataType = dataType
    currStanza.lines.append(currLine)    
   
    # Check for the longest line in the hymn (to determine page placement)
    currWidth = canvas.stringWidth(currLine.data, fontName, fontSize)
    if (currWidth > hymn.maxLineWidth):
      hymn.maxLineWidth = currWidth

  # Add the final stanza in
  hymn.stanzas.append(currStanza)

  lineCount = 0
  for stanza in hymn.stanzas:
    for line in stanza.lines:
      lineCount += 1

  # Load the index of first lines and choruses
  global hymnIndex  #Modifying a global variable
  hymnIndex.append((hnum, "firstline", hymn.stanzas[0].lines[0].data)) #First line
  for stanza in hymn.stanzas:
    if stanza.isChorus:
      hymnIndex.append((hnum, "chorus", stanza.lines[0].data)) #First Chorus
      break
  #Sort the index list
  hymnIndex = sorted(hymnIndex, key=lambda h: h[2].lower())


  # Total height of the hymn : not needed any more, height is calculated based on actual drawing on a temp page
  # Height of all the stanzas, and their gaps, plus the header
  #hymn.hymnHeight = (lineCount * fontLeading) + ((len(hymn.stanzas)-1)*stanzaYGap) + hymnHeaderFontLeading + hymnHeaderYSpaceBelow

  return hymn


def printHymnData(d):
  print "Hymn "+str(d.hnum)
  for stanza in d.stanzas:
    print "Stanza "+stanza.stanza
    for line in stanza.lines:
      print (line.indent*" ") + line.data+" : "+line.dataType

# Called when a hymn is extending over a page break
# Returns the new y position on the page
def breakHymnOverPage(x, y, hymnNumber):
  canvas.setFont(fontName, fontSize-4)
  canvas.drawCentredString(pageWidth/2, y, "(Continued)")
  y = newPageY(y) 
  y -= (hymnHeaderFontLeading + hymnHeaderYSpaceBelow) # leave the top of the page for hymn headers, continued hymns don't use the header
  #canvas.setFont(hymnHeaderFontName, hymnHeaderFontSize)
  #canvas.drawString(leftMargin, y, str(hymnNumber)+" continued")
  #y -= (hymnHeaderFontLeading + hymnHeaderYSpaceBelow)
  return y


def drawHymn(hymnData, startYPos, hymnCount):
  y = startYPos
  
  #Setup the hymn number
  hnum = hymnData.hnum
  hymnNumber = hnum
  if renumber: 
    hymnNumber = hymnCount
  # If we're renumbering, then we need to store the new number 
  # This can be used later for conversions from hnum -> new num
  hymnData.hymnNumber = hymnNumber
    

  # If the stanza has two digits, make extra space for that
  thisStanzaNumIndent = stanzaNumIndent
  if hymnData.twoDigitStanza:
   thisStanzaNumIndent += (fontSize * 0.5) # widen it by a letter width approx

  # Center the hymn based on the longest line in the hymn
  # x is the left side main drawing position (stanza names will be indented to the left of this)
  x = leftMargin + (thisStanzaNumIndent / 2) + ((maxLineWidth - hymnData.maxLineWidth) / 2)

  # Used to delay the drawing of the hymn header until we determine if the first stanza will make the page wrap
  firstStanza = 1

  # For each stanza in this hymn
  for stanza in hymnData.stanzas:
    stanzaHeight = len(stanza.lines) * fontLeading
    
    #Check if we're running out of space on the page (first stanzas are checked later, more strictly)
    if not firstStanza:
      if ((y - stanzaHeight) <= yBottomOfPage):
        y = breakHymnOverPage(x, y, hymnNumber)

    # Draw the hymn header info
    if firstStanza:
      # If there is more than one stanza, ensure the first stanza fits (plus the continued text)
      if len(hymnData.stanzas) > 1:   # fontLeading for the continued text, hymnHeader for the Hymn number and space
        if y - (stanzaHeight + (fontLeading*2) + (hymnHeaderFontLeading+hymnHeaderYSpaceBelow)) <= yBottomOfPage:
          y = newPageY(y)
 
      canvas.setFont(hymnHeaderFontName, hymnHeaderFontSize)
      canvas.drawString(leftMargin, y, str(hymnNumber))
      y -= (hymnHeaderFontLeading + hymnHeaderYSpaceBelow)
      firstStanza = 0
   
    # Draw the stanza number in the left margin
    if stanza.isChorus: 
      indent = chorusIndent
    else: 
      indent = 0
      if not stanza.stanza.startswith('s'):
        #Draw the stanza number (left of the margin)
        drawHymnLine(x-thisStanzaNumIndent, y, stanza.stanza, hnum)
    
    # Draw the lines of this stanza
    for line in stanza.lines:
      drawHymnLine(x+indent, y, line.data, hnum)
      y -= fontLeading
      
    y -= stanzaYGap # Gap for a new stanza

  # Remove the last stanzaYGap, this is just wasted space, as there is no next stanza  
  y += stanzaYGap

  #Mark this hymn as added
  hymnData.added  = True

  # Some gap between this hymn and the next one
  y -= ySpaceBetweenHymns   

  return y



# Find the best match hymn for the specified amount of height
def getLongestHymnLessThan(height, allHymnData):
  bestHymnHeight = 0
  bestHymn = False
  for h in allHymnData:
    if ((h.hymnHeight > bestHymnHeight) and (h.hymnHeight < height) and (h.added == False)):
      bestHymnHeight = h.hymnHeight
      bestHymn = h
  return bestHymn


# Get the smallest hymn that has not yet been drawn
def getSmallestHymnHeight(allHymnData):
  smallestHymnHeight = 9999999.99
  for h in allHymnData:
    if (h.hymnHeight < smallestHymnHeight) and (h.added == False):
      smallestHymnHeight = h.hymnHeight
  return smallestHymnHeight


# Returns the number the hymn drew with, either the hnum or the new num
def getNumFromHnum(hnum, allHymnData):
  # If we're not renumbering then it's easy, just the hnum
  if not renumber:
    return hnum
  # Go through all the hymns and lookup this hnum
  for h in allHymnData:
    if h.hnum == hnum:
      return h.hymnNumber     
  raise Exception("No hymn found with hnum="+str(hnum)+" in allHymnData")


# The first page, the title, pretty static
def drawTitlePage():
  canvas.setFont(titleFontName, titleFontSize)
  canvas.drawCentredString(pageWidth/2, yTopOfPage-100 , "Songbook")
  canvas.drawCentredString(pageWidth/2, yTopOfPage-150, "")
  canvas.drawCentredString(pageWidth/2, yTopOfPage-250, "")
  # Go to the next page, but don't do the page numbering or increment pageCount 
  canvas.showPage()

  # Add a blank page after the title page (page 1 is on the right side then)
  if insertBlankPageAfterTitlePage: 
    canvas.showPage()


# Draw the Index pages
def drawIndexOfFirstLinesAndChoruses(initialY, allHymnData):
  # Start a new page
  y = newPageY(initialY)
  
  # To control the pagination when printing as a booklet
  if insertBlankPageBeforeIndex:
    newPage()
  if insertSecondBlankPageBeforeIndex:
    newPage()  

  # Draw the title
  canvas.setFont(titleFontName, titleFontSize)
  canvas.drawCentredString(pageWidth/2, y, "Index of First Lines and Choruses")
  y -= titleFontLeading + 10 # some space looks nicer

  # Go through and draw each index entry
  for entry in hymnIndex:
    hnum = entry[0]
    entryType = entry[1] 
    line = entry[2]
    
    # Get the display number this hymn drew with
    num = getNumFromHnum(hnum, allHymnData)

    # Check for space on the page for this line
    if y <= (bottomMargin + fontLeading): # Leave a little extra space at the bottom
      y = newPageY(y)

    # Setup the fonts
    lineFontName = fontName
    if entryType=="chorus":
      lineFontName = lineFontName+"-Oblique" # Like italics?
    
    # Draw the FirstLine or Chorus text
    canvas.setFont(lineFontName, fontSize)
    canvas.drawString(leftMargin, y, line)

    # Draw the Hymn Number
    lineWidth = canvas.stringWidth(line, lineFontName, fontSize)
    canvas.setFont(fontName+"-Bold", fontSize)
    canvas.drawString(leftMargin + lineWidth + fontSize, y, str(num))
 
    y -= fontLeading


# ---------------- Main ---------------------

# Get the data for all the hymns
allHymnData = []
song_list = (1083, 1725, 1086, 507, 497, 513, 643, 812, 1008, 1113, 1151, 1159, 1162, 1170,
  1178, 1179, 1191, 1724, 1700, 1926, 1732, 1717, 1753, 1810, 2000, 2800,
  2509, 1237, 1226, 1232, 1331, 1600, 2128, 2312, 2712,  # added for the second edition May 2011
  9999, 1308, 1131, 1079, 1333, 322, 2606, 1716, 723, 2130, 2844, 1340 )
#for hnum in range(1,200):
for hnum in song_list:
  allHymnData.append(loadHymnData(hnum))
 

# -------------- Determine the actual printing height of each hymn -----------------------
# Done by printing each hymn on a temp canvas, the real printing will be done later
y = yTopOfPage
hymnCount = 1
for i, hymn in enumerate(allHymnData):
  # Draw this hymn on the page
  yBeforeDrawing = y
  pageCountBeforeDrawing = pageCount
  y = drawHymn(hymn, y, hymnCount)
  y += ySpaceBetweenHymns # Don't include the spacer in the height calculations
  hymn.pagesUsed = (pageCount - pageCountBeforeDrawing) + 1 
  hymn.ySpaceLeft = y - yBottomOfPage
  hymn.hymnHeight = ((hymn.pagesUsed-1) * maxPageHeight) + (maxPageHeight - hymn.ySpaceLeft) 
  y = newPageY(y)

# Save and close the temp canvas
canvas.save()
# Delete the temp file
os.remove(tempFileName)

# -- reset all the added flags--
for h in allHymnData:
  h.added = False


# ------------------------ Final Drawing ---------------------------
# Draw the hymns on the final canvas
canvas = Canvas(fileName, pagesize=letter)
pageCount = 1  # Global, used to keep track of which page we're on 
y = yTopOfPage

#Header Page, pretty static
drawTitlePage()


hymnCount = 1
for i, hymn in enumerate(allHymnData):

  # If the hymn has already been drawn, then don't draw it again!
  if hymn.added:
    continue

  # Variables to determine drawing
  # How much space is left on the page
  spaceLeft = y - yBottomOfPage 
  # True if it's a left page, false if it's a right page 
  leftPage = ((pageCount % 2) == 0) 
  #if we inserted a blank page, page 1 is on the left 
  if not insertBlankPageAfterTitlePage: 
    leftPage = not leftPage # If page 1 is on the left, reverse this calculation

  #Smallest hymn not yet drawn
  smallestHymnHeight = getSmallestHymnHeight(allHymnData)

  #Set to False as necessary below 
  waitForPageBreak = True
     # If the hymn fits on this page, good let's draw it
  if ((spaceLeft > hymn.hymnHeight) or
     # If the hymn is more than two pages, then it will wrap whatever we do, so just draw it
     (hymn.pagesUsed > 2) or
     # If we're already at the top of a left page, that's all we can do
     (leftPage and (y == yTopOfPage)) or
     # On a left page, and it will fit into this and the next page (when it wraps remove the header that is wasted)
     ((leftPage and ((spaceLeft + (maxPageHeight - (hymnHeaderFontLeading + hymnHeaderYSpaceBelow))) > hymn.hymnHeight)) and
     # And it will leave enough space for another hymn, or this hymn is more than 1 page long 
     ((smallestHymnHeight < ((spaceLeft+maxPageHeight)-(hymn.hymnHeight+(fontLeading*4)))) or (hymn.pagesUsed > 1)))):
    waitForPageBreak = False
    print "nobreak leftPage="+str(leftPage)+" spaceLeft="+str(spaceLeft)+" height="+str(hymn.hymnHeight)+" smallestHymn="+str(smallestHymnHeight)
    print "smallestHymnCompare :"+str((spaceLeft+maxPageHeight)-(hymn.hymnHeight+(fontLeading*3)))  

  # If we decided we can't draw this hymn right now, try to fill in the space before we draw it
  if waitForPageBreak == True:
    spaceAvailable = spaceLeft

    if (leftPage and hymn.pagesUsed == 2):
      spaceAvailable += (maxPageHeight - (fontLeading*4)) # 4 lines added for a stanza wrap on the page break
    print "Waiting for page break on hnum="+str(hymn.hnum)+" in spaceAvailable="+str(spaceAvailable)
    
    #Find a suitable hymn to fill the space
    hymnToDraw = getLongestHymnLessThan(spaceAvailable, allHymnData)
    if hymnToDraw:
      drawHymn(hymnToDraw, y, hymnCount)
      hymnCount += 1
      print "Fit hymn "+str(hymnToDraw.hnum)+" with height="+str(hymnToDraw.hymnHeight)
    # Force a page break
    y = newPageY(y)
    print "doing page break"

 
  # Draw this hymn on the page
  y = drawHymn(hymn, y, hymnCount)
  hymnCount += 1
  print "Drew hymn "+str(hymn.hnum)+" y="+str(y)


# Draw the Index pages
drawIndexOfFirstLinesAndChoruses(y, allHymnData)


# Print the footer info for the last page
printFooter()
# Close the Canvas, we're done
canvas.save()

print "maxPageHeight="+str(maxPageHeight)
