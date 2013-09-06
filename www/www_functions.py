# Functions for WWW stuff 
import cgi, re, time


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
  if  (param.strip() == ""): return "" #An int is valid if it's left blank
  if (not re.match("[\-0-9]+", param)):
    param = ""
  return param

def getTime():
  return int(round(time.time() * 1000))

