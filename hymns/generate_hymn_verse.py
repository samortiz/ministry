#!/usr/bin/env python
# This will generate HTML files to be used to convert to iSilo format for viewing on handhelds
import os, shutil, pg, re 
from db_functions import *

# Setup 
dir = "hymn_verse_html"

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
  retHtml = "<span>"
  SQL = "select id, ref, fn, par from hymn_verse where hnum='"+hnum+"' and stanza='"+stanza+"' and line='"+line+"' "
  
  hymnVerses = db.query( SQL).getresult()
  for hymnVerse in hymnVerses :
    hymn_verse_id = toString(hymnVerse[0])
    ref = toString(hymnVerse[1])
    noteNum = toString(hymnVerse[2])
    notePar = toString(hymnVerse[3])
    retHtml += (" <span style='font-weight:bold; font-size:80%; white-space:nowrap'>"+
                "<a name='ref_"+hymn_verse_id+"' href='#verse_"+hymn_verse_id+"'>"+
                genRefHtml(ref, noteNum, notePar)+"</a></span>")
    hymnVerseEntries.append((hymn_verse_id,  ref, noteNum, notePar))
  retHtml += "</span>"
  
  if (retHtml == "<span></span>") : retHtml = ""
  return retHtml


def getKeyVerseRefHTML(hnum, key) :
  "This will return the HTML for the key verse (specified by the key number)) "
  retHtml = "<span>"
  SQL = "select id, ref, fn, par from hymn_verse where hnum='"+hnum+"' and key='"+key+"' "

  hymnVerses = db.query( SQL).getresult()
  for hymnVerse in hymnVerses :
    hymn_verse_id = toString(hymnVerse[0])
    ref = toString(hymnVerse[1])
    noteNum = toString(hymnVerse[2])
    notePar = toString(hymnVerse[3])

    retHtml += (" <span style='font-weight:bold; font-size:80%; white-space:nowrap'>" +
      "<a name='ref_key_"+hymn_verse_id+"' href='#verse_key_"+hymn_verse_id+"'>"+genRefHtml(ref, noteNum, notePar)+"</a></span>")
    hymnVerseEntries.append((hymn_verse_id,  ref, noteNum, notePar, "key_"))
  retHtml += "</span>"
  
  if (retHtml == "<span></span>") : retHtml = ""
  return retHtml

def createHymnFile(hnum, html):
  "Create or replace the file for this hymn, using the specified html for content, and the hnum for the filename."
  fileName = dir+"/"+hnum+".html"
  file = open(fileName,"w")
  file.write(html)
  file.close()
  print "created "+fileName




# Create the root directory
if (not os.path.exists(dir)) : 
  os.makedirs(dir)

# Go through all the hymns we have verses entered for
for songNum in range(1,2855):
  row= dbGetRow("select hnum, chinese_num, spanish_num, korean_num, tagalog_num, calgary_songbook_num from hymn where hnum="+str(songNum))
  # If no row is found for this hymn, then it's not a valid song number (calgary songbook is non-sequential)
  if (len(row) == 0): 
    html = "<html>Song #"+str(songNum)+" does not exist.</html>"
    createHymnFile(toString(songNum).rjust(4,'0'), html)
    continue # Do not do any further processing, just create a stub file
  
  hnum = toString(row[0]).rjust(4,'0')
  chinese_num= toString(row[1])
  spanish_num= toString(row[2])
  korean_num= toString(row[3])
  tagalog_num= toString(row[4])
  calgary_songbook_num = toString(row[5])
  hymnVerseEntries = [] # Stores a list of tuples (hymn_verse_id, ref)  both are strings
  
  html = "<html>"
  if (int(hnum) <= 1348) : 
    html += "<center>E<b>"+str(int(hnum))+"</b> C<b>"+chinese_num+"</b> K<b>"+korean_num+"</b> S<b>"+spanish_num+"</b> T<b>"+tagalog_num+"</b></center>"
  else: 
    html += "<center><b>#"+hnum+"</b></center>"
    
  # Display the Key (number 1) verse (if there is one)
  verseHtml = getKeyVerseRefHTML(hnum, "1")
  if (verseHtml != "") : html += verseHtml 
  
  #Display the verses not associated to any stanza or line
  verseHtml = getVerseRefHTML(hnum, "", "")
  if (verseHtml != ""): html += verseHtml + "<br>\n"
  
  currStanza = ""
  lastLine = "0"  #Stores the previous line, so we can tell when two "s" stanza's back to back end (the line count goes back to 1)
  firstChorus = 1 # Set to 0 after the first chorus is over
  
  # Get all the lines of the hymn
  hymnHtml = ""
  hymnLines = db.query("select stanza, line, data, type from hymn_line where hnum="+hnum+" and line!='' order by id").getresult()
  for hymnLine in hymnLines :
    stanza = toString(hymnLine[0])
    line = hymnLine[1]
    data  = toString(hymnLine[2])
    type = toString(hymnLine[3])
    
    if ((currStanza != stanza) | (int(lastLine) > int(line))): # We are switching to a new stanza
      if (currStanza != "") : hymnHtml += "</div>\n" # Close the prev stanza (unless there was none)
      # Start the new stanza
      if (re.match("[c][1-9]{0,1}",stanza)) :  # If it's a chorus then indent it
        hymnHtml  += "<div style='padding-left:8px; padding-top:8px; ' >\n" # chorus
        if (firstChorus | (currStanza != "c")):  # Only add verse stuff to the first chorus (so it's not repeated), only if it's a "c" chorus, if it's c2 c3 etc then it's a different chorus
          stanzaRefHtml = getVerseRefHTML(hnum, stanza, "")
          if (stanzaRefHtml != ""): 
            hymnHtml += stanzaRefHtml +"<br>\n"
      else : 
        hymnHtml += "<div style='padding-left:1px; padding-top:8px;'>\n"  # regular verse
        if (stanza != "s") : 
          stanzaRefHtml = getVerseRefHTML(hnum, stanza, "")
          if (stanzaRefHtml != ""): hymnHtml += stanzaRefHtml+"<br>\n"
          hymnHtml += "<b>"+stanza+"</b> "
        
      if (currStanza == "c") : firstChorus = 0 # If we are switching out of a chorus, then don't do the chorus stuff again
      currStanza = stanza
      
    # Write out this hymn line
    if (type == "data"): 
      hymnHtml += "<span style='white-space:nowrap'>"+data+"</span>"
    elif (type == "tune"): 
      hymnHtml += "<span style='white-space:nowrap'>Tune : "+data+"</span>"
    elif ((type == "ref") | (type == "comment")): 
      hymnHtml += "<span style='white-space:nowrap'>"+data+"</span>"
    elif (type == "info"): 
      hymnHtml += "<span style='white-space:nowrap; font-style:italic'>"+data+"</span>"
    
    # Only fail to draw the hymn verse references when it is a non-first chorus
    if ((firstChorus == 1) | (currStanza !="c")) :  hymnHtml += getVerseRefHTML(hnum, stanza, line) 
    hymnHtml += "<br>\n"
    lastLine = line # Store this line number, so we can see if it's incrementing properly in the next iteration (multiple s stanzas can reset the line counter)
   
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
      "<a name='verse_"+key+hymn_verse_id+"' href='#ref_"+key+hymn_verse_id+"'>"+hymn_verse_ref+"</a></span>")

    # Add the verse text
    verseTexts = db.query("select v.verse from verse v, hymn_verse_verse hvv where "+
      " hvv.hymn_verse_id="+hymn_verse_id+" and hvv.verse_id = v.id  order by v.id").getresult()
    for verseText in verseTexts:
      txt = toString(verseText[0])
      verseHtml += " "+txt
    
    #lookup the footnote text 
    if (hymn_verse_fn != ""): 
      noteSQL = (
          "select n.verse_note "+
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
        if (firstNote == 0): noteHtml += "<br>"
        else: firstNote = 0
        noteHtml += note_text
        
      # Add the note reference (if necessary) and text
      verseHtml += "<br><b>fn "+hymn_verse_fn+" "
      if (hymn_verse_par != ""): verseHtml += "par "+hymn_verse_par+" "
      verseHtml += "</b>"
      verseHtml += noteHtml 


    verseHtml += "<br><div style='height:5px'></div>\n"
  verseHtml += "</div>"
  # If there are no verses, then don't bother with the verseHTML
  if (len(hymnVerseEntries) == 0): verseHtml = "" 


  # Create the main HTML display
  html += hymnHtml
  if (verseHtml != ''):
    html += "<hr>\n"
    html += verseHtml
  
  html += "<br><br><br><br><br><br><br>"

  html += "</html>\n"
   
  #Generate the file 
  createHymnFile(hnum, html)
  


