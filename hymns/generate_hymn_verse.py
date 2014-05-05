#!/usr/bin/env python
# This will generate HTML files to be used to convert to iSilo format for viewing on handhelds
import sys, os, shutil, pg, re 
from db_functions import *
from file_functions import *

# Stores firstlines and choruses. contains [data, hnum]
firstLines = []

# Get output dir (parameter)
output_dir = "build/hymn_verse_html"
if (len(sys.argv) >= 2) :
  output_dir = sys.argv[1]

# Create the output directory if necessary
if (not os.path.exists(output_dir)) : 
  os.makedirs(output_dir)
  print "Creating directory "+output_dir

# Get the verses parameter
withVerses = True
if (len(sys.argv) >= 3) :
  withVerses = (sys.argv[2] != "noverses")

# Get the fileExtension parameter
fileExtension = "html"
if (len(sys.argv) >= 4) :
  fileExtension = sys.argv[3]

imagePath = "images/"
navPath = ""
navPathFromRoot = ""
pagePath = ""
rootPath = ""
if (fileExtension == "xhtml"):
  imagePath = "../images/"
  navPath = "../nav/"
  navPathFromRoot = "nav/"
  pagePath = "pages/"
  rootPath = "../" 
  if (not os.path.exists(output_dir+"/pages")):
    os.makedirs(output_dir+"/pages")

# ---- Helper functions ----
def genRefHtml(ref, num, par):
    "Generate a reference with the footnote and paragraph in superscript as needed"
    if (num == ""): return ref
    #If we have a footnote
    retHtml = ref+"<sup>"+num
    if (par != ""): retHtml += "p"+par
    retHtml += "</sup>"
    return retHtml
  

def getVerseRefHTML(hnum, stanza, line):
  "This will return the HTML for the verse reference for the specified hymn, stanza and line"
  if (not withVerses) :
    return ""

  retHtml = "<span>"
  SQL = "select id, ref, fn, par from hymn_verse where hnum='"+hnum+"' and stanza='"+stanza+"' and line='"+line+"' "
  
  hymnVerses = db.query( SQL).getresult()
  for hymnVerse in hymnVerses :
    hymn_verse_id = toString(hymnVerse[0])
    ref = toString(hymnVerse[1])
    noteNum = toString(hymnVerse[2])
    notePar = toString(hymnVerse[3])
    retHtml += (" <span class='verse'>"+
                "<a id='ref_"+hymn_verse_id+"' href='#verse_"+hymn_verse_id+"'>"+
                genRefHtml(ref, noteNum, notePar)+"</a></span>")
    hymnVerseEntries.append((hymn_verse_id,  ref, noteNum, notePar))
  retHtml += "</span>"
  
  if (retHtml == "<span></span>") : retHtml = ""
  return retHtml


def getKeyVerseRefHTML(hnum, key) :
  "This will return the HTML for the key verse (specified by the key number)) "
  if (not withVerses):
    return ""

  retHtml = "<span>"
  SQL = "select id, ref, fn, par from hymn_verse where hnum='"+hnum+"' and key='"+key+"' "

  hymnVerses = db.query( SQL).getresult()
  for hymnVerse in hymnVerses :
    hymn_verse_id = toString(hymnVerse[0])
    ref = toString(hymnVerse[1])
    noteNum = toString(hymnVerse[2])
    notePar = toString(hymnVerse[3])

    retHtml += (" <span class='verse'>" +
      "<a id='ref_key_"+hymn_verse_id+"' href='#verse_key_"+hymn_verse_id+"'>"+genRefHtml(ref, noteNum, notePar)+"</a></span>")
    hymnVerseEntries.append((hymn_verse_id,  ref, noteNum, notePar, "key_"))
  retHtml += "</span>"
  
  if (retHtml == "<span></span>") : retHtml = ""
  return retHtml

def createHymnFile(hnum, html) :
  "Create or replace the file for this hymn, using the specified html for content, and the hnum for the filename."
  fileName = output_dir+"/"+pagePath+hnum+"."+fileExtension
  #print "Generating page "+fileName
  writeStringToFile(fileName, html)


# Go through all the hymns
print "Generating pages for hymns"
hymns = dbQuery("select hnum, chinese_num, spanish_num, korean_num, calgary_songbook_num from hymn order by hnum")
for hymn in hymns:
  hnum = toString(hymn[0]).rjust(4,'0')
  chinese_num= toString(hymn[1])
  spanish_num= toString(hymn[2])
  korean_num= toString(hymn[3])
  calgary_songbook_num = toString(hymn[4])
  hymnVerseEntries = [] # Stores a list of tuples (hymn_verse_id, ref)  both are strings
  
  #Calculate next/prev 
  prevHnum = dbGetOne("select hnum from hymn where hnum < "+hnum+" order by hnum desc limit 1")
  nextHnum = dbGetOne("select hnum from hymn where hnum > "+hnum+" order by hnum limit 1")

  #Draw the page header
  html = ""
  if (fileExtension == "xhtml"):
    html += '<?xml version="1.0" encoding="utf-8" ?>\n'
    html += '<html xmlns="http://www.w3.org/1999/xhtml">\n'
    html += '<head>\n'
    html += '<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>\n'
    html += '<title>Hymn '+hnum+'</title>\n'
    html += "<link href='../stylesheet.css' rel='stylesheet' type='text/css'/>\n"
  else :
    html += "<html>\n"
    html += "<head>\n"
    html += "<link href='stylesheet.css' rel='stylesheet' type='text/css'/>\n"

  html += "</head>\n"
  html += "<body>\n"
  
  html += "<div style='text-align:center'>\n"
  if (prevHnum) :
    html += "<a href='"+prevHnum.rjust(4,'0')+"."+fileExtension+"' class='hidden_a'><b> &lt; </b></a>\n"
  
  html += "<a href='"+navPath+"nav_0000."+fileExtension+"' class='hidden_a'>\n"
  if (int(hnum) <= 1348) : 
    html += "E<b>"+str(int(hnum))+"</b> C<b>"+chinese_num+"</b> K<b>"+korean_num+"</b> S<b>"+spanish_num+"</b>\n"
  else: 
    html += "<b>"+hnum+"</b>\n"
  html += "</a>\n"
  
  if (nextHnum) :
    html += " <a href='"+nextHnum.rjust(4,'0')+"."+fileExtension+"' class='hidden_a'><b> &gt; </b></a>\n"
  html += "</div>\n"


  #Display the verses not associated to any stanza or line
  verseHtml = getVerseRefHTML(hnum, "", "")
  if (verseHtml != "") : 
    html += "<div>"+verseHtml+"</div>\n"
  else : # If there are no song-wide verses then we will use a key verse
    # Display the Key (number 1) verse (if there is one)
    verseHtml = getKeyVerseRefHTML(hnum, "1")
    if (verseHtml != "") : 
      html += "<div>"+verseHtml+"</div>\n"
  
  currStanza = "~BEGIN~"
  lastLine = "0"  #Stores the previous line, so we can tell when two "s" stanza's back to back end (the line count goes back to 1)
  firstChorus = 1 # Set to 0 after the first chorus is over
  firstLine = 1 # Set to 0 after the first line is over

  # Get all the lines of the hymn
  hymnHtml = ""
  hymnLines = db.query("select stanza, line, data, type from hymn_line where hnum="+hnum+" and line!='' order by lineorder").getresult()
  for hymnLine in hymnLines :
    stanza = toString(hymnLine[0])
    line = hymnLine[1]
    data  = toString(hymnLine[2])
    lineType = toString(hymnLine[3])

    #Escape XML / HTML characters in the data
    data = data.replace("&", "&amp;")

    #Store the firstline
    if (firstLine and (lineType == "data")) :
      firstLines.append([data, hnum, "firstline"])
    
    if ((currStanza != stanza) | (int(lastLine) > int(line))): # We are switching to a new stanza
      if (currStanza != "~BEGIN~") : hymnHtml += "</div>\n" # Close the prev stanza (unless there was none)
      # Start the new stanza
      if (re.match("[c][1-9]{0,1}",stanza)) :  # If it's a chorus then indent it
        hymnHtml  += "<div class='chorus'>\n" # chorus
        #Add the first chorus to the list
        if (firstChorus) :
          firstLines.append([data, hnum, "chorus"])
        if (firstChorus | (currStanza != "c")):  # Only add verse stuff to the first chorus (so it's not repeated), only if it's a "c" chorus, if it's c2 c3 etc then it's a different chorus
          stanzaRefHtml = getVerseRefHTML(hnum, stanza, "")
          if (stanzaRefHtml != ""): 
            hymnHtml += "<div>"+stanzaRefHtml +"</div>\n"
        # Start drawing the line (chorus markings go in the line)
        hymnHtml += "<div class='line'>"
      else : 
        hymnHtml += "<div class='stanza'>\n"  # regular verse
        # Start drawing the line (chorus markings go in the line)
        hymnHtml += "<div class='line'>"
        if (stanza != "s") : 
          stanzaRefHtml = getVerseRefHTML(hnum, stanza, "")
          if (stanzaRefHtml != ""): hymnHtml += "<div>"+stanzaRefHtml+"</div>\n"
          # Start drawing the line (chorus markings go in the line)
          hymnHtml += "<b>"+stanza+"</b> "
      if (currStanza == "c") : firstChorus = 0 # If we are switching out of a chorus, then don't do the chorus stuff again
      currStanza = stanza
    # This is a regular line, not starting a new stanza
    else:
      hymnHtml += "<div class='line'>"

    # Write out this hymn line
    hymnHtml += data
    
    # Only fail to draw the hymn verse references when it is a non-first chorus
    if ((firstChorus == 1) | (currStanza !="c")) :  hymnHtml += getVerseRefHTML(hnum, stanza, line) 
    hymnHtml += "</div>\n" #line
    lastLine = line # Store this line number, so we can see if it's incrementing properly in the next iteration (multiple s stanzas can reset the line counter)
    
    # First line is the first line of data (not references or comments etc)
    if (lineType == "data") :
      firstLine = 0

  hymnHtml += "</div>\n" # Close the final stanza  
  
  # Write out the verses 
  verseHtml = "<div style='padding-left:10px'>"
  for hymnVerseEntry in hymnVerseEntries:
    hymn_verse_id = hymnVerseEntry[0]
    hymn_verse_ref = hymnVerseEntry[1]
    hymn_verse_fn = hymnVerseEntry[2]
    hymn_verse_par = hymnVerseEntry[3]
    key = ""
    if (len(hymnVerseEntry) > 4):  key = hymnVerseEntry[4]
    
    
    verseHtml += ("<span style='white-space:nowrap; font-weight:bold'>"+
      "<a id='verse_"+key+hymn_verse_id+"' href='#ref_"+key+hymn_verse_id+"'>"+hymn_verse_ref+"</a></span>")

    # Add the verse text
    verseTexts = db.query("select v.verse from verse v, hymn_verse_verse hvv where "+
      " hvv.hymn_verse_id="+hymn_verse_id+" and hvv.verse_id = v.id  order by v.id").getresult()
    for verseText in verseTexts:
      txt = toString(verseText[0])
      verseHtml += " "+txt
    
    #lookup the footnote text 
    if (hymn_verse_fn != ""): 
      noteSQL = (
          "select n.note "+
          "from verse_note n,  hymn_verse_verse hvv "+
          "where n.verse_id = hvv.verse_id "+
          "  and hvv.hymn_verse_id = "+hymn_verse_id+" "+
          "  and n.num = '"+hymn_verse_fn+"' " )
      if (hymn_verse_par != ""): noteSQL += "  and (n.par='"+hymn_verse_par+"' or n.par='') "
      notes = db.query(noteSQL).getresult()
      noteHtml = ""
      firstNote = 1
      for note in notes:
        note_text = toString(note[0])
        if (firstNote == 0): 
          noteHtml += "<div/>\n"
        else: 
          firstNote = 0
        noteHtml += note_text
        
      # Add the note reference (if necessary) and text
      verseHtml += "<div/><b>fn "+hymn_verse_fn+" "
      if (hymn_verse_par != ""): verseHtml += "par "+hymn_verse_par+" "
      verseHtml += "</b>"
      verseHtml += noteHtml 


    verseHtml += "<div style='height:5px'></div>\n"
  verseHtml += "</div>\n"
  # If there are no verses, then don't bother with the verseHTML
  if (len(hymnVerseEntries) == 0): verseHtml = "" 


  # Create the main HTML display
  html += hymnHtml
  if (verseHtml != '') or (fileExtension=="xhtml"):
    html += "<div style='height:10px; padding-bottom:10px; border-bottom:1px solid black; margin:0px 30px'>&#160;</div>\n"
    html += verseHtml
  
  if (fileExtension == "html"):
    html += "<div style='padding-bottom:40px'>&#160;</div>\n"

  html += "</body></html>\n"
   
  # Generate the hymn file (page) 
  createHymnFile(hnum, html)
 



# Create the index file with first lines and choruses
firstLinesHtml = ""

#First make a sort column (Strip all non-alphanumeric characters for the sort)
for line in firstLines :
  sortLine = line[0].replace(" ", "1")
  sortLine = re.sub(r'\W+', '', sortLine).upper()
  #Adjust all the Oh to sort with O
  if sortLine.startswith("OH1") :
    sortLine = sortLine[:1] + sortLine[(2):]
  line.insert(0,sortLine)

firstLines.sort()
currLetter = ""
allLetters = []
prevLine = ["","","",""]
for line in firstLines :
  sort = line[0]
  data = line[1]
  hnum = line[2]
  lineType = line[3]
  dataHtml = ""
  if (lineType == "chorus") :
    dataHtml = "<i>"+data+"</i>"
  else :
    dataHtml = data

  #Check for duplicate lines (don't need to include them twice)
  if ((prevLine[0] == line[0]) and (prevLine[2] == line[2])):
    continue
  else :
    prevLine = line

  #Add Letter headings
  if (currLetter != sort[0]) :
    currLetter = sort[0]
    allLetters.append(currLetter) #Store for making links
    firstLinesHtml += "<div style='padding-top:15px; text-align:center'><b><a id='"+currLetter+"' href='#top' class='hidden_a'>"+currLetter+"</a></b></div>\n"

  #Generate the line to display
  firstLinesHtml += "<div>\n"+\
      "<a href='"+pagePath+hnum+"."+fileExtension+"' class='hidden_a'>\n"+\
      "<img src='images/bullet.gif' alt='-'/> "+dataHtml+" <b>"+hnum.lstrip("0")+"</b>\n"+\
      "</a></div>\n"

#Setup the page header
header = ""
if (fileExtension == "xhtml"):
  header += '<?xml version="1.0" encoding="utf-8" ?>\n'
  header += '<html xmlns="http://www.w3.org/1999/xhtml">\n'
  header += '<head>\n'
  header += '<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>\n'
  header += '<title>Hymn '+hnum+'</title>\n'
  header += '</head>\n'
else:
 header += "<html>\n"

header += "<body>\n"
header += "<div>\n"
header += "<a id='top'></a><div style='text-align:center; padding-bottom:10px'>\n"
header += "<a href='"+navPathFromRoot+"nav_0000."+fileExtension+"' class='hidden_a'>Index of First Lines and Choruses</a></div>\n"
header += "<div style='text-align:center'>\n"
for letter in allLetters :
  header += "<a class='hidden_a' href='#"+letter+"'>"+letter+"</a>\n"  
header += "</div>\n"
firstLinesHtml = header + firstLinesHtml + "<div style='height:30px'></div></div>\n</body></html>"

#Output the firslines file
fileName = output_dir+"/firstlines."+fileExtension
print "Generating "+fileName
writeStringToFile(fileName, firstLinesHtml)

