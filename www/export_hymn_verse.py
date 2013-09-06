#!/usr/bin/env python
# Export a hymn to a spreadsheet
import cgi, re
from db_functions import *

# Get the CGI hnum (if there is one, otherwise export all the hymns)
hnum = ""
form = cgi.FieldStorage() # parse query
if form.has_key("hnum"): 
  hnum = form["hnum"].value
  if (not re.match("[0-9]{1,4}", hnum)): hnum = ""

if (hnum == ""): fileName = "hymn_export.xls"
else: fileName = "hymn_"+hnum+"_export.xls"

print "Content-Type:application/excel; name=\""+fileName+"\" ";
print "Content-Disposition: attachment; filename=\""+fileName+"\"\r\n";


html = "<html>"
html += "<body>"
html += "<table border=0 cellspacing=0 cellpadding=0>"

html += "<thead>"
html += "<tr>"
html += "<td>Hymn</td>"
html += "<td>Stanza</td>"
html += "<td>Line</td>"
html += "<td>Verse</td>"
html += "<td>FN</td>"
html += "<td>Par</td>"
html += "<td>Key</td>"
html += "<td>Min_Ref</td>"
html += "<td>Min_Quote</td>"
#html += "<td>Completed_By</td>"
#html += "<td>Verified_By</td>"
html += "</tr>"
html += "</thead>"
html += "<tbody>"

#Setup the SQL for exporting
SQL = "select hnum, stanza, line, ref, fn, par, key, min_ref, min_quote, completed_by, verified_by from hymn_verse"
if (hnum != ""): SQL += " where hnum="+hnum
SQL += " order by hnum, stanza, line, fn, par"

hymnVerses = db.query(SQL).getresult()
for hymnVerse in hymnVerses:
  hnum = toString(hymnVerse[0])
  stanza = toString(hymnVerse[1])
  line = toString(hymnVerse[2])
  ref = toString(hymnVerse[3])
  fn = toString(hymnVerse[4])
  par = toString(hymnVerse[5])
  key = toString(hymnVerse[6])
  min_ref = toString(hymnVerse[7])
  min_quote = toString(hymnVerse[8])
  completed_by = toString(hymnVerse[9])
  verified_by = toString(hymnVerse[10])
  
  html += "<tr>"
  html += "<td>"+hnum+"</td>"
  html += "<td>"+stanza+"</td>"
  html += "<td>"+line+"</td>"
  html += "<td>"+ref+"</td>"
  html += "<td>"+fn+"</td>"
  html += "<td>"+par+"</td>"
  html += "<td>"+key+"</td>"
  html += "<td>"+min_ref+"</td>"
  html += "<td>"+min_quote+"</td>"
  #html += "<td>"+completed_by+"</td>"
  #html += "<td>"+verified_by+"</td>"
  html += "</tr>"
  
html += "</tbody>"
html += "</table>"
html += "</body></html>"

print html
