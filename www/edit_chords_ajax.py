#!/usr/bin/env python
import cgi, re, json
from db_functions import *
from verse_functions import *

print "Content-type: text/html\n"

#Parse the query parameters 
form = cgi.FieldStorage()


def getParam(paramName):
  "Returns the parameter value matching the paramName as a string.  Returns empty string if no parameter is found"
  param = ""
  if form.has_key(paramName):
    param = form[paramName].value
  return param

def getIntParam(paramName):
  "This will return the parameter value matching the paramName, as a string, but will ensure the value is a valid integer or it returns empty string."
  global foundError, errMsg
  param = getParam(paramName)
  if  (param.strip() == ""): return "" #An int is valid (no error) if it's left blank
  if (not re.match("[0-9]{1,4}", param)): 
    foundError = 1
    errMsg += paramName+"="+param+" which is not a valid integer. "
    param = ""
  return param




# Variables
foundError = 0
errMsg = ""
chordHtml = "" # Response HTML for the client to draw the new chord

# Get the parameter info
hnum = getIntParam("hnum")
hymn_line_id = getIntParam("hymn_line_id") # "" will mean insert a new oneilne
chpos = getIntParam("chpos")
chord = getParam("chord")
mode = getParam("mode")

#Initcap the chord
if (chord != ""): 
  chord = chord[0].upper() + chord[1:]

#Error Checking
if (hnum == ""):
  foundError = 1
  errMsg = "No hnum specified!"
  
if ((chord != "") and (not re.match("^[A-G](b|#)?(m(aj)?|M|aug|dim|sus)?([2-7]|9|13)?(\/[A-G](b|#)?)?$", chord))) :
  foundError = 1
  errMsg = chord+" is not a valid chord!"

if (hymn_line_id == ""): 
  foundError = 1
  errMsg = "No hymn_line_id was specified"

if not foundError: 
  hymnLine = dbGetOne("select data from hymn_line where id="+hymn_line_id)
  if (hymnLine == ""): 
    foundError = 1
    errMsg = "Hymn line not found in the databse with hymn_line_id="+hymn_line_id
  
if ((not foundError) and (int(chpos) >= len(hymnLine))):
  foundError = 1
  errMsg = "Hymn line is only "+toString(len(hymnLine))+" characters long, you cannot specify position "+chpos
  
#Create the client-side HTML reference display
chordHtml += "<span style='position:relative'><div style='position:absolute; top:-32px; left:-1px; font-weight:bold;'>"
chordHtml += chord
chordHtml += "</div></span>"

#Delete a chord
if ((not foundError) and (mode == "del")): 
  db.query("delete from hymn_line_chord where hymn_line_id="+hymn_line_id+" and pos="+chpos)
  
#insert the chord into the database
elif ((not foundError) and (chord != "")):
  db.query("insert into hymn_line_chord (hnum, hymn_line_id, pos, chord) values ('"+hnum+"', '"+hymn_line_id+"', '"+chpos+"', '"+chord+"') ")
  
  
 #Output to the client 
print json.dumps({"foundError":foundError
                        , "errMsg":errMsg
                        , "hymn_line_id":hymn_line_id
                        , "chpos":chpos
                        , "chord":chord
                        , "chordHtml":chordHtml
                        })
  
