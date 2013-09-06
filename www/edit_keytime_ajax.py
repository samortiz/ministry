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
retKey = "" # response value for the client
retTime = "" #response value for the client

# Get the parameter info
hnum = getIntParam("hnum")
key = getParam("key")
time = getParam("time")
mode = getParam("mode")

#Error Checking
if (hnum == ""):
  foundError = 1
  errMsg = "No hnum specified!"
  
if ((key != "") and (not re.match("^[a-gA-G](b|#)?(m)?(\-[1-9])?$", key))) :
  foundError = 1
  errMsg = key+" is not a valid key signature!  You should use a letter for the key with an optional capo eg. G-2"

if ((time != "") and (not re.match("^[1-8]/[1-8]$", time))) :
  foundError = 1
  errMsg = time+" is not a valid time signature! It should look like '3/4' or '4/4' "

if (key != "") : 
  key = key[0].upper() + key[1:]

if not foundError: 
  if (mode == "key"): 
    db.query("update hymn set key='"+escape(key)+"' where hnum="+hnum)
    retKey = key

  if (mode == "time"): 
    db.query("update hymn set time_signature='"+escape(time)+"' where hnum="+hnum)
    retTime = time
  
  
  
 #Output to the client 
print json.dumps({"foundError" : foundError
                        , "errMsg" : errMsg
                        , "key" : retKey
                        , "time" : retTime
                        })
  
