#!/usr/bin/env python
import os, shutil, pg, cgi, re, json
from db_functions import *

print "Content-type: text/html\n"
html = ""
headHtml = """
<script type="text/javascript" src="jxs.js"></script>
<script type="text/javascript" src="PopupWindow.js"></script>
<script type="text/javascript" src="edit_hymn.js"></script>
"""

html += """
<!-- Popup Div -->
<DIV ID="popup_div" STYLE="position:absolute; visibility:hidden; background-color:#F1F9FF; padding:2px; border:1px solid black; border-right:2px solid black; border-bottom:2px solid black;"> 
 <table border=0 cellspacing=0 cellpadding=1>
 <form name='divform' method='get' action='javascript:submitPopupGeneric()'> 
 <tr><td>Reference</td><td><input id='ref' name='ref'  type='text' size=20></td></tr>
 <tr><td>Footnote</td><td>#<input id='fn' name='fn' type='text' size=2> p<input id='par' name='par' type='text' size=2></td</tr>
 <tr><td>Key </td><td>#<input id='key' name='key' type='text' size=2></td</tr>
 <tr><td>Min Ref</td><td><input id='min_ref' name='min_ref' type='text' size=20></td><tr>
 <tr><td valign='top'>Min Quote</td><td><textarea id='min_quote' name='min_quote' cols=30 rows=4></textarea></td></tr>
  <tr><td>Comment</td><td><input id='comment' name='comment' type='text' size=20></td</tr>
 <tr><td colspan='100%' align='center'>
  <input type='submit' id='popup_submit' name='popup_submit' value='Submit'  style='display:none'>
  <input type='button' onClick="submitPopup('add')" id='add_button' name='add_button' value='Add'> 
  <input type='button' onClick="submitPopup('edit')" id='edit_button' name='edit_button' value='Edit'>  &nbsp; 
  <input type='button' onClick="submitPopup('delete')" name='delete' value='Delete'> &nbsp; 
  <input type='button' onClick="submitPopup('cancel')" name='cancel' value='Cancel'>
  </td></tr>
 </form></table>
 </DIV>

<form name='theform' method='get' action='edit_hymn.py'>
"""

hymnVerseEntries = [] # Stores a list of tuples (hymn_verse_id, ref)  both are strings
hymnHtml = ""
verseHtml = ""

# ---- Helper functions ----
def getVerseRefHTML(hnum, stanza, line):
  "This will return the HTML for the verse reference for the specified hymn, stanza and line"
  retHtml = "<span id='stanza_"+stanza+"_"+line+"'>"
  hymnVerses = db.query("select id, ref, fn, par from hymn_verse where hnum='"+hnum+"' and stanza='"+stanza+"' and line='"+line+"' order by id").getresult()
  for hymnVerse in hymnVerses :
    hymn_verse_id = toString(hymnVerse[0])
    ref = toString(hymnVerse[1])
    noteNum = toString(hymnVerse[2])
    notePar = toString(hymnVerse[3])
    
    hymnVerseEntries.append((hymn_verse_id,  ref, noteNum, notePar))
    retHtml += " <span id='hymn_ref_"+hymn_verse_id+"' style='font-weight:bold; font-size:80%; white-space:nowrap'>"+ref
    if (noteNum != ""): 
      retHtml += "<sup>"+noteNum
      if (notePar != ""): retHtml += "p"+notePar
      retHtml += "</sup>"
    retHtml += "</span>"
    
  #Close the all references span
  retHtml += "</span>"
  return retHtml



# --------------- Main ------------------------
hnum = ""
form = cgi.FieldStorage() # parse query
if form.has_key("hnum"): 
  hnum = form["hnum"].value
  if (not re.match("[0-9]{1,4}", hnum)): hnum = ""


# -------- Draw the navigation -------
html += "Hymn #"
html += "<input type='text' name='hnum' method='get' value='"+hnum+"' size=3 >"
html += " <input type='submit' name='submit' value='Go'> "
if (hnum != "") : 
  html += " <a href='export_hymn_verse.py?hnum="+hnum+"'>Export</a> (click this, and send the file to Sam for inclusion in the master copy) "
  html += getVerseRefHTML(hnum, "", "")
html += "<br>\n"


if hnum != "": 
  currStanza = ""
  firstChorus = 1 # Set to 0 after the first chorus is over

  # -- Setup the javascript data storage object for all the hymn_verse entries for this hymn
  hymnLines = db.query("select id, hnum, stanza, line, ref, fn, par, key, min_ref, min_quote, comment from hymn_verse where hnum="+hnum).getresult()
  headHtml += ("<script language='javascript'>var data="+json.dumps(hymnLines)+";\n data.sort(dataComparator); </script>\n")

  # ----- Get all the lines of the hymn -----
  hymnLines = db.query("select stanza, line, data from hymn_line where hnum="+hnum+" order by lineorder").getresult()
  for hymnLine in hymnLines :
    stanza = toString(hymnLine[0])
    line = hymnLine[1]
    data  = toString(hymnLine[2])
    
    if ((currStanza != stanza) or (line == "1")) : # We are switching to a new stanza
      if (currStanza != "") : hymnHtml += "</div>\n" # Close the prev stanza (unless there was none)
      # Start the new stanza
      if (stanza == "c") : 
        hymnHtml  += "<div style='padding-left:20px; padding-top:10px; padding-bottom:10px'>\n" # chorus
        if firstChorus: hymnHtml += getVerseRefHTML(hnum, stanza, "")
      else : 
        hymnHtml += "<div style='padding:10px'>\n"  # regular verse
        if (stanza != "s") : 
          hymnHtml += stanza + getVerseRefHTML(hnum, stanza, "")
      
      #Draw the + sign to add hymnVerse entries on the stanza 
      if ((firstChorus == 1 and stanza == "c") or ((stanza != "s") and (stanza != "c")) ): 
        hymnHtml += ("<A HREF='javascript:addHymnVerse(\""+hnum+"\",\""+stanza+"\",\"\")' name='add_"+hnum+"_"+stanza+"_' id='add_"+hnum+"_"+stanza+"_' "+
                   " style='font-weight:bold; text-decoration:none; color:#00FF55'>+</a> <br>")
      
      if (currStanza == "c") : firstChorus = 0 # If we are switching out of a chorus, then don't do the chorus stuff again
      currStanza = stanza
      
    # Write out this hymn line
    hymnHtml += "<span style='white-space:nowrap'>"+data+"</span>"
    # Only fail to draw the hymn verse references when it is a non-first chorus
    if ((firstChorus == 1) | (currStanza !="c")) :  
      hymnHtml += getVerseRefHTML(hnum, stanza, line) 
      hymnHtml += ("<A HREF='javascript:addHymnVerse(\""+hnum+"\",\""+stanza+"\",\""+line+"\")' name='add_"+hnum+"_"+stanza+"_"+line+"' id='add_"+hnum+"_"+stanza+"_"+line+"' "+
                   " style='font-weight:bold; text-decoration:none; color:#00FF55'>+</a>")
    hymnHtml += "<br>\n"
  
  hymnHtml += "</div>\n" # Close the final stanza  
  
  
  # ----- Write out the verses  -----
  verseHtml += "<div id='verselist' style='padding-left:10px'>"
  for hymnVerseEntry in hymnVerseEntries:
    hymn_verse_id = hymnVerseEntry[0]
    hymn_verse_ref = hymnVerseEntry[1]
    hymn_verse_fn = hymnVerseEntry[2]
    hymn_verse_par = hymnVerseEntry[3]
    
    verseHtml += "<span id='hymn_verse_"+hymn_verse_id+"'>" #Used to remove verse entries
    verseHtml += "<a href='javascript:editHymnVerse("+hymn_verse_id+")' id='edit_"+hymn_verse_id+"' name='edit_"+hymn_verse_id+"'><b>Edit</b></a> "
    verseHtml += "<span style='white-space:nowrap; font-weight:bold'>"+hymn_verse_ref+"</span>"
    
    #Add the verse text
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
        if (firstNote == 0): noteHtml += "<br>"
        else: firstNote = 0
        noteHtml += note_text
        
      # Add the note reference (if necessary) and text
      verseHtml += "<br><b>fn "+hymn_verse_fn+" "
      if (hymn_verse_par != ""): verseHtml += "par "+hymn_verse_par+" "
      verseHtml += "</b>"
      verseHtml += noteHtml 
    
    verseHtml += "<div style='height:5px'></div>"
    verseHtml += "</span>\n" 
    
  verseHtml += "</div>\n"
  
html += ("<table border=0 cellspacing=0 cellpadding=0><tr>"+
    " <td valign='top'>"+hymnHtml+"</td>"+
    " <td valign='top'>"+verseHtml+"</td>"+
    "</tr></table>")
  
  
html += "</form>\n"

print "<html><head>"+headHtml+"</head>\n\n\n<body>"+html+"</body></html>"
