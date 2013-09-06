#!/usr/bin/env python
import os, shutil, pg, cgi, re, json
from db_functions import *


print "Content-type: text/html\n"
html = ""

hymnHtml = ""

# --------------- Main ------------------------
hnum = ""
form = cgi.FieldStorage() # parse query
if form.has_key("hnum"): 
  hnum = form["hnum"].value
  if (not re.match("[0-9]{1,4}", hnum)): hnum = ""


# -------- Draw the navigation -------
html += "<form name='theform' method='post' action='display_hymn.py'>"
html += "Hymn #"
html += "<input type='text' name='hnum' method='get' value='"+hnum+"' size=3 >"
html += " <input type='submit' name='submit' value='Go'> "
html += "</form><br>\n"


if hnum != "": 
  currStanza = ""
  firstChorus = 1 # Set to 0 after the first chorus is over

  # ----- Get all the lines of the hymn -----
  hymnLines = db.query("select stanza, line, data, indent from hymn_line where hnum="+hnum+" order by lineorder").getresult()
  for hymnLine in hymnLines :
    stanza = toString(hymnLine[0])
    line = hymnLine[1]
    data  = toString(hymnLine[2])
    indent = hymnLine[3]
    
    if ((currStanza != stanza) or (line == "1")) : # We are switching to a new stanza
      if (currStanza != "") : hymnHtml += "<br>\n" # Close the prev stanza (unless there was none)
      # Start the new stanza
      if (stanza == "c") : 
        hymnHtml  += "" # chorus
      else : 
        hymnHtml += ""  # regular verse
        if (stanza != "s") : 
          hymnHtml += "<b>"+stanza+"</b> "
      
      if (currStanza == "c") : firstChorus = 0 # If we are switching out of a chorus, then don't do the chorus stuff again
      currStanza = stanza
      
    if (currStanza == "c") : hymnHtml += "&nbsp;&nbsp;"

    # Write out this hymn line
    hymnHtml += indent * "&nbsp;"
    hymnHtml += "<span style='white-space:nowrap'>"+data+"</span><br>"
  
  hymnHtml += "<br>\n" # Close the final stanza  
  
html += hymnHtml 

print "<html><body>"+html+"</body></html>"
