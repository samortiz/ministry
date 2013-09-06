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

def getVerseId(ref) :
  return dbGetOne("select id from verse where ref='"+ref+"'")



# Variables
foundError = 0
errMsg = ""
refHtml = "" # Response HTML for the client to draw the reference 
verseHtml = ""  #Response HTML, for the client to draw the verses (including the reference, verses, footnotes, ministry quote, comments)
verseIds = [] # contains verse_id strings for inserting into the database

# Get the parameter info
hymn_verse_id = getIntParam("hymn_verse_id") # "" will mean insert a new one
hnum = getIntParam("hnum")
stanza = getParam("stanza")
line = getIntParam("line")
ref = getParam("ref")
fn = getIntParam("fn")
par = getIntParam("par")
key = getIntParam("key")
min_ref = getParam("min_ref")
min_quote = getParam("min_quote")
comment = getParam("comment")


#Validate the reference
fixedRef = fixRef(ref)
if (not validRef(fixedRef)) : 
  foundError = 1
  errMsg = "Invalid Reference : '"+ref+"'. "
ref = fixedRef
  
#Now we know it's a reasonable looking reference, try to get the verse id(s)
if not foundError:
  # Check to see if it's a single verse (otherwise it's a range)
  if validRefSingle(ref):
    verse_id = getVerseId(ref)
    if (verse_id == ""):
      foundError = 1
      errMsg = ref+" does not exist!"
    else: 
      verseIds.append(verse_id)
      
  else: # We have a range of verses
    #Calculate the start verse and the end verse
    startVerse = str(re.match("^([123]{0,1}[ ]{0,1}[A-Za-z]{1,10} [0-9]{0,3}[:]{0,1}[0-9]{0,3})[ ]{0,1}-.*$", ref).group(1))
    endChapVerse = str(re.match("^.* *- *([0-9]{0,3}[:]{0,1}[0-9]{1,3})$", ref).group(1))
    if (not re.match(".*:.*", endChapVerse)) : # If the ending ref does not have a chapter
      # Get the chapter from the starting verse ref
      endChap = str(re.match("^[123]{0,1}[ ]{0,1}[A-Za-z]{1,10} ([0-9]{0,3})[:]{0,1}[0-9]{0,3}.*$", ref).group(1))
      if (re.match(".*:.*",ref)): # If there is no : in the entire reference, then we can ignore the chapters altogether (don't add the chapter in)
        endChapVerse = endChap+":"+endChapVerse
    # The book that these verses are in
    endBook = str(re.match("^([123]{0,1}[ ]{0,1}[A-Za-z]{1,10}) .*$", ref).group(1))
    endVerse = endBook+" "+endChapVerse
    # Get the ids for the starting and ending verses (they are all sequential)
    startVerseId = getVerseId(startVerse)
    endVerseId = getVerseId(endVerse)
    
    if (startVerseId==""): 
      foundError = 1
      errMsg = startVerse+" is not a valid reference."
    if (endVerseId==""):
      foundError = 1
      errMsg = endVerse+" is not a valid reference."
    if (fn != ""): 
      foundError = 1
      errMsg += "You cannot specify a footnote with a range of verses, you must choose a single verse. "
    if (foundError == 0):
      for verseId in range(int(startVerseId), int(endVerseId)+1):
        verseIds.append(toString(verseId))
        


#If there is no footnote, then there shouldn't be any paragraph entry
if (foundError == 0) & (par != "") & (fn == ""): 
  foundError = 1
  errMsg = "You cannot specify a paragraph without specifying a footnote!"

#Create the client-side HTML reference display
refHtml += "<span style='white-space:nowrap; font-weight:bold'>"+ref
if (fn != ""): 
  refHtml += "<sup>"+fn
  if (par != ""): refHtml += "p"+par
  refHtml += "</sup>"
refHtml += "</span>"

#Get the verse text to send back to the client
if (foundError == 0) :
  verseHtml += refHtml
  for verse_id in verseIds:
    verseText = dbGetOne("select verse from verse where id='"+verse_id+"'")
    verseHtml += " "+verseText

#lookup the footnote text 
if ((foundError == 0) & (fn != "")):
  verse_id = verseIds[0] # Choose the first verse
  noteHtml = ""
  noteSQL = (
          "select n.note "+
          "from verse_note n "+
          "where n.verse_id = "+verse_id+
          "  and n.num = '"+fn+"' " )
  if (par != ""): noteSQL += " and n.par='"+par+"' "
  notes = db.query(noteSQL).getresult()
  firstNote = 1
  if (len(notes) == 0):
    foundError = 1
    errMsg += "No footnote "+fn+" "
    if (par != ""): errMsg += "with paragraph "+par+" "
    errMsg += "found for "+ref+". "
  for note in notes:
    note_text = toString(note[0])
    if (firstNote == 0): noteHtml += "<br>"
    else: firstNote = 0
    noteHtml += note_text
   
    # Add the note reference (if necessary) and text
    verseHtml += "<br><b>fn "+fn+" "
    if (par != ""): verseHtml += "par "+par+" "
    verseHtml += "</b>"
    verseHtml += noteHtml 



#Insert the data into the database
if (foundError == 0) :
  #Insert the data into the database
  if (hymn_verse_id == ""): 
    hymn_verse_id = dbGetOne("select nextval('hymn_verse_id_seq')")
    db.query("insert into hymn_verse (id, hnum, stanza, line, ref, fn, par, key, min_ref, min_quote, comment, import_batch) values "+ 
        "('"+hymn_verse_id+"', '"+hnum+"', '"+stanza+"', '"+line+"', '"+escape(ref)+"','"+escape(fn)+"', '"+escape(par)+"', '"+escape(key)+
       "','"+escape(min_ref)+"','"+escape(min_quote)+"','"+escape(comment)+"','online') ") 
  else:
    db.query("update hymn_verse set "+
         "  ref='"+escape(ref)+"' "+
         ", fn='"+escape(fn)+"' "+
         ", par='"+escape(par)+"' "+
         ", key='"+escape(key)+"' "+
         ", min_ref='"+escape(min_ref)+"' "+
         ", min_quote='"+escape(min_quote)+"' "+
         ", comment='"+escape(comment)+"' "+
         ", import_batch = import_batch || ':'||now() "+
         ", import_date=now() "+
         "where id="+hymn_verse_id) 
         
  for verse_id in verseIds:
    db.query("delete from hymn_verse_verse where hymn_verse_id="+hymn_verse_id)
    db.query("insert into hymn_verse_verse (hymn_verse_id, verse_id) values ('"+hymn_verse_id+"', '"+verse_id+"') ") 


print json.dumps({"foundError":foundError
                        , "errMsg":errMsg
                        , "hnum":hnum
                        , "stanza":stanza
                        , "line":line
                        , "ref":ref
                        , "key":key
                        , "fn":fn
                        , "par":par
                        , "min_ref":min_ref
                        , "min_quote":min_quote
                        , "comment":comment
                        , "refHtml":refHtml
                        , "verseHtml":verseHtml 
                        , "hymn_verse_id":hymn_verse_id
                        })
  

  
