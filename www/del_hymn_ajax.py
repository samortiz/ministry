#!/usr/bin/env python
import cgi, re, json
from db_functions import *
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
  param = getParam(paramName)
  if (not re.match("[0-9]{1,4}", param)): param = ""
  return param


# Variables
foundError = 0
errMsg = ""
hnum = ""
stanza = ""
line = ""

hnum = getIntParam("hnum")
hymn_verse_id = getIntParam("hymn_verse_id")

data = db.query("select hnum, stanza, line from hymn_verse where id='"+hymn_verse_id+"'").getresult()
if (len(data) == 0):
  foundError = 1
  errMsg = "no entry found for hymn_verse_id="+hymn_verse_id
else:
  hnum = toString(data[0][0])
  stanza = toString(data[0][1])
  line = toString(data[0][2])
  
if foundError == 0:
  db.query("delete from hymn_verse where id='"+hymn_verse_id+"'")

print json.dumps({"foundError":foundError, "errMsg":errMsg, "hnum":hnum, "stanza":stanza})
  

  
