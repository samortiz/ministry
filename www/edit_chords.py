#!/usr/bin/env python
import os, shutil, pg, cgi, re, json
from db_functions import *

print "Content-type: text/html\n"
html = ""
headHtml = """
<script type="text/javascript" src="jxs.js"></script>
<script type="text/javascript" src="PopupWindow.js"></script>
<script type="text/javascript" src="edit_chords.js"></script>

<style>
  .quickchord {
    border:1px solid black;
  }

  .quickchord td {
    padding-top:2px;
    padding-bottom:2px;
    padding-left : 5px;
    padding-right : 5px;
    color: blue;
    text-align:center;
  }
  
  .hymnline { 
    white-space : nowrap; 
    padding-top : 20px; 
    font-size : 16px 
  } 
  .hymnline span {
    position : relative;
  }
  .hymnline div {
    position : absolute; 
    top : -32px;
    left : -1px;
    font-weight : bold;
  }
  .hymnline a {
    text-decoration : none;
    color : black;
    border : none;
  }

</style>

"""


hymnVerseEntries = [] # Stores a list of tuples (hymn_verse_id, ref)  both are strings
hymnHtml = ""
verseHtml = ""
html += "<form name='mainform' method='get' action='edit_chords.py'>"

# --------------- Main ------------------------
hnum = ""
form = cgi.FieldStorage() # parse query
if form.has_key("hnum"): 
  hnum = form["hnum"].value
  if (not re.match("[0-9]{1,4}", hnum)): hnum = ""

# --  Setup the hnum javascript
headHtml += "<script language='javascript'>var hnum = '"+hnum+"';</script>"

# -------- Draw the navigation -------
html += "Hymn #"
html += "<input type='text' name='hnum' method='get' value='"+hnum+"' size=3 >"
html += " <a href='javascript:document.forms[0].submit()'>Go</a><br>\n"

# ----- Draw the Quick Chords ----
html += """
<div style='position:absolute; right:0; top:0; text-align:center '>
   <b>Quick Chords </b> : 
  <span onclick="setChord('X')" id='quickchord_X' style='color:blue;'>Off</span>
  
 <table border=0 cellspacing=0 cellpadding=0 class='quickchord'>
 <tr>
  <td onclick="setChord('A')" id='quickchord_A'>A</td>
  <td onclick="setChord('B')" id='quickchord_B'>B</td>
  <td onclick="setChord('C')" id='quickchord_C'>C</td>
  <td onclick="setChord('D')" id='quickchord_D'>D</td>
  <td onclick="setChord('E')" id='quickchord_E'>E</td>
  <td onclick="setChord('F')" id='quickchord_F'>F</td>
  <td onclick="setChord('G')" id='quickchord_G'>G</td>
 </tr>
 <tr>
  <td onclick="setChord('Am')" id='quickchord_Am'>Am</td>
  <td onclick="setChord('Bm')" id='quickchord_Bm'>Bm</td>
  <td onclick="setChord('Cm')" id='quickchord_Cm'>Cm</td>
  <td onclick="setChord('Dm')" id='quickchord_Dm'>Dm</td>
  <td onclick="setChord('Em')" id='quickchord_Em'>Em</td>
  <td onclick="setChord('Fm')" id='quickchord_Fm'>Fm</td>
  <td onclick="setChord('Gm')" id='quickchord_Gm'>Gm</td>
</tr>
 <tr>
  <td onclick="setChord('A7')" id='quickchord_A7'>A7</td>
  <td onclick="setChord('B7')" id='quickchord_B7'>B7</td>
  <td onclick="setChord('C7')" id='quickchord_C7'>C7</td>
  <td onclick="setChord('D7')" id='quickchord_D7'>D7</td>
  <td onclick="setChord('E7')" id='quickchord_E7'>E7</td>
  <td onclick="setChord('F7')" id='quickchord_F7'>F7</td>
  <td onclick="setChord('G7')" id='quickchord_G7'>G7</td>
 </tr>
<tr>
  
  <td onclick="setChord('F#m')" id='quickchord_F#m'>F#m</td>
  <td onclick="setChord('C#m')" id='quickchord_C#m'>C#m</td>
</tr>
  
 </table></div>""";

if hnum != "": 
  
  #Draw the links to edit the key 
  key = dbGetOne("select key from hymn where hnum="+hnum)
  if (key == "") : key = "None"
  hymnHtml += "Key : <a href='javascript:showPopupKey()' id='key_anchor'>"+key+"</a> &nbsp;"
 
  #Draw the links to edit the time
  time = dbGetOne("select time_signature from hymn where hnum="+hnum)
  if (time == ""): time = "None"
  hymnHtml += "Time : <a href='javascript:showPopupTime()' id='time_anchor'>"+time+"</a><br>"
  


  currStanza = ""
  firstChorus = 1 # Set to 0 after the first chorus is over

  # ----- Get all the lines of the hymn -----
  hymnLines = db.query("select id, stanza, line, data from hymn_line where hnum="+hnum+" order by lineorder").getresult()
  for hymnLine in hymnLines :
    hymn_line_id = toString(hymnLine[0])
    stanza = toString(hymnLine[1])
    line = hymnLine[2]
    data = toString(hymnLine[3])
    
    if ((currStanza != stanza) or (line == "1")) : # We are switching to a new stanza
      if (currStanza != "") : hymnHtml += "</div>\n" # Close the prev stanza (unless there was none)
      # Start the new stanza"
      if (stanza == "c") : 
        hymnHtml  += "<div style='padding-left:20px; padding-top:10px; padding-bottom:10px'>\n" # chorus
      else : 
        hymnHtml += "<div style='padding:10px'>\n"  # regular verse
      
      if (currStanza == "c") : firstChorus = 0 # If we are switching out of a chorus, then don't do the chorus stuff again
      currStanza = stanza
      
    # Write out this hymn line
    hymnHtml += "<div class='hymnline'>"
    
    #Get the chord data
    chordDataRs = db.query("select pos, chord from hymn_line_chord where hymn_line_id="+hymn_line_id).getresult()
    chordData = {} # Stores chords keyed on character position
    for chordRow in chordDataRs :
      chordData[chordRow[0]] = chordRow[1]
      
    #Loop variables
    chPos = 0 #counter, character position in the line
    inChord = 0 # Set to 1 when we are inside a chord eg. [A]
     
    # Go through each character in the line
    for ch in data : 
      hymnHtml += "<span><a href=\"javascript:delChord('"+hymn_line_id+"', '"+toString(chPos)+"')\">"
      hymnHtml += "<div id='chord_hymn_line_id"+hymn_line_id+"_chpos"+toString(chPos)+"'>"
      #If this position has a chord associated
      if (chPos in chordData):
        chord = chordData[chPos]
        hymnHtml += chord
      hymnHtml += "</div></a></span>"
      
      # Draw the character of the hymn line
      hymnHtml += "<a href=\"javascript:showPopup('"+hymn_line_id+"', '"+toString(chPos)+"')\" id='a_hymn_line_id"+hymn_line_id+"_chpos"+toString(chPos)+"'>"+ch+"</a>"
      chPos = chPos + 1
    
    
    hymnHtml += "</div>\n" #Close the hymnline div
  
  hymnHtml += "</div>\n" # Close the final stanza  

# Draw the page (put all the html chunks together)

html += hymnHtml
html += "</form>\n" 

#the popup needs to be below the rest so the absolute divs in the popup will be "on top" of the other absolute divs
html += """
<!-- Popup Div for chords -->
<DIV ID="popup_div" STYLE="position:absolute; visibility:hidden; background-color:#F1F9FF; padding:2px; 
 border:1px solid black; border-right:2px solid black; border-bottom:2px solid black;"> 
 <table border=0 cellspacing=0 cellpadding=0>
 <form name='divform' method='post' action='javascript:doNothing()'> 
<tr><td nowrap>Chord <input id='chord' name='chord'  type='text' size=2 onblur='submitPopup()'></td></tr>
 </form></table>
 </DIV>

<!-- Popup Div  for Key -->
<DIV ID="key_popup_div" STYLE="position:absolute; visibility:hidden; background-color:#F1F9FF; padding:2px; 
 border:1px solid black; border-right:2px solid black; border-bottom:2px solid black;"> 
 <table border=0 cellspacing=0 cellpadding=0>
 <form name='keydivform' method='post' action='javascript:doNothing()'> 
<tr><td nowrap>Key<input id='key' name='key'  type='text' size=4 onblur='submitKey()'></td></tr>
 </form></table>
 </DIV>
 
<!-- Popup Div  for Time-->
<DIV ID="time_popup_div" STYLE="position:absolute; visibility:hidden; background-color:#F1F9FF; padding:2px; 
 border:1px solid black; border-right:2px solid black; border-bottom:2px solid black;"> 
 <table border=0 cellspacing=0 cellpadding=0>
 <form name='timedivform' method='post' action='javascript:doNothing()'> 
<tr><td nowrap>Time<input id='time' name='time'  type='text' size=4 onblur='submitTime()'></td></tr>
 </form></table>
 </DIV>
"""  



print "<html><head>"+headHtml+"</head>\n\n\n<body>"+html+"</body></html>"
