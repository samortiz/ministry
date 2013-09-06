#!/usr/bin/env python
#This script goes through the HTML files for the hymns and stores the text in a postgres database
import urllib, sgmllib,pg, re

class MyParser(sgmllib.SGMLParser):
  "Parse Strongs XML and put it in the database."

  def parse(self, s):
    "Parse the given string 's'."
    self.feed(s)
    self.close()

  def __init__(self, verbose=0):
    "Initialise an object, passing 'verbose' to the superclass."
    sgmllib.SGMLParser.__init__(self, verbose)
    self.entries = [] 

    self.inEntry = 0
    self.strongs_num = 0
    self.entry_text = ""
    self.greek = ""
    self.unicode = ""
    self.translit = ""
    self.pronunciation = ""
    self.inStrongsDerivation = 0
    self.strongs_derivation = ""
    self.strongsref_language = ""
    self.strongsref_strongs = ""
    self.inStrongsDef = 0
    self.strongs_def = ""
    self.inKJV = 0
    self.KJV = ""
    self.inStrongs = 0
    self.seeList = [] #Array of pairs

  def start_entry(self, attributes):
    "Handles : <entry strongs='00003'> "
    self.inEntry = 1
    for name, value in attributes:
      if (name=="strongs"):
        self.strongs_num = value

  def end_entry(self):
    "Close entry tag"
    self.inEntry = 0

    #Cleanup data 
    # There seems to be a strange :-- in front of each KJV and a . at the end - Trim them off!
    if re.match("^:--", self.KJV):
      self.KJV = self.KJV[3:len(self.KJV)-1] # Trim off the leading :--
    if re.match("\.$", self.KJV):
      self.KJV = self.KJV[:len(self.KJV)-1] #Trim off the trailing .
  
    #Remove multiple consecutive whitespace (and trailing/leading whitespace)
    whitespacePattern = re.compile('[ ]{2,}')
    self.entry_text = whitespacePattern.sub(' ', self.entry_text).strip()
    self.strongs_derivation = whitespacePattern.sub(' ', self.strongs_derivation).strip()
    self.strongs_def =  whitespacePattern.sub(' ', self.strongs_def).strip()
    self.KJV =  whitespacePattern.sub(' ', self.KJV).strip()
    
    #Display the data we have collected
    print "Entry "+self.strongs_num+" greek="+self.greek+" pron="+self.pronunciation+" unicode="+self.unicode+" translit="+self.translit
    print "  derv="+self.strongs_derivation
    print "  def="+self.strongs_def
    print "  kjv="+self.KJV
    print "  txt="+self.entry_text
    for see in self.seeList : 
      print "  see={Strongs #"+see[0]+" "+see[1]+"}"
    print ""

    #Write all the data to the database
    db.query("insert into strongs (num, lemma, unicode, translit, pronunciation, derivation, def, kjv_def, entry) values "+
      "('"+self.strongs_num+"', '"+escape(self.greek)+"', '"+escape(self.unicode)+"', '"+escape(self.translit)+"', '"+escape(self.pronunciation)+"', '"+escape(self.strongs_derivation)+"', '"+escape(self.strongs_def)+"', '"+escape(self.KJV)+"', '"+escape(self.entry_text)+"');")
    for see in self.seeList :
      db.query("insert into strongs_see (strongs_num, see_strongs_num, see_strongs_language) values "+
        "('"+self.strongs_num+"', '"+see[0]+"', '"+see[1]+"');")

    # Clear all the data fields (to start a new entry)
    self.inEntry = 0
    self.strongs_num = 0
    self.entry_text = ""
    self.greek = ""
    self.unicode = ""
    self.translit = ""
    self.pronunciation = ""
    self.inStrongsDerivation = 0
    self.strongs_derivation = ""
    self.strongsref_language = ""
    self.strongsref_strongs = ""
    self.inStrongsDef = 0
    self.strongs_def = ""
    self.inKJV = 0
    self.KJV = ""
    self.inStrongs = 0
    self.seeList = [] #Array of pairs


  def start_strongs(self, attributes):
    "contains text with the strongs number, which we don't need (we have it in the entry tag) "
    self.inStrongs = 1
  def end_strongs(self):
    self.inStrongs = 0
 

  def start_greek(self, attributes):
    "Handles :  <greek BETA='*)ABILHNH' unicode='xxx' translit='xxx' /> "
    for name, value in attributes:
      if name=="beta":
        greek = value
      elif name=="unicode":
        unicode = value
      elif name=="translit":
        translit=value
    # A display of the greek tag, for inserting into text strings
    greekDisplay = "{greek "+greek+"}"

    # If we're in a deriv or def tag, then add the greek word there, otherwise it's the base word   
    if self.inStrongsDerivation == 1:
      self.strongs_derivation += greekDisplay
    elif self.inStrongsDef == 1:
      self.strongs_def += greekDisplay
    elif self.greek != "" :  #There already exists a greek defition, then it's another greek tag, just display ig
      self.entry_text += greekDisplay
    else : 
      self.greek = greek
      self.unicode = unicode
      self.translit = translit



  def start_pronunciation(self, attributes):
    "Handles : <pronunciation strongs='ab-ee-ath'-ar'/>"
    if self.inStrongsDef == 0 and self.inStrongsDerivation == 0 :
      for name, value in attributes:
        if (name=="strongs"):
          self.pronunciation = value



  def start_strongs_derivation(self, attributes):
    "contains text and <strongsref> tags "
    self.inStrongsDerivation = 1
  def end_strongs_derivation(self):
    self.inStrongsDerivation = 0

  def start_strongsref(self, attributes):
    "handles strongsref tags inside strongs_derivation tags "
    # Get the values of the tag (there is no closing tag)
    for name, value in attributes:
      if (name=="language"):
        self.strongsref_language = value
      elif name=="strongs":
        self.strongsref_strongs = value
    # Construct the display string for strongsref (links)    
    refDisplay = "{Strongs #"+self.strongsref_strongs+" "+self.strongsref_language.lower()+"}"

    # Add the strongsref syntax to the appropriate parent tag
    if self.inStrongsDerivation == 1 :
      self.strongs_derivation += refDisplay
    elif self.inStrongsDef == 1:
      self.strongs_def += refDisplay
    elif self.inKJV == 1 :
      self.KJV += refDisplay
    else :
      self.entry_text += refDisplay
  

  def start_strongs_def(self, attributes):
    self.inStrongsDef = 1
  def end_strongs_def(self):
    self.inStrongsDef = 0

  def start_kjv_def(self, attributes):
    self.inKJV = 1
  def end_kjv_def(self):
    self.inKJV = 0

  def start_see(self, attributes):
    "store see tags in an array (multiple) : <see language='GREEK' strongs='242'/>"
    for name, value in attributes:
      if (name=="language"):
        language = value.lower()
      elif (name=="strongs"):
        strongs = value
    self.seeList.append((strongs, language))



  def handle_data(self, data):
    "Handle the text within tags"
    if self.inStrongsDerivation == 1 : 
      self.strongs_derivation += data  
    elif self.inStrongsDef == 1 :
      self.strongs_def += data
    elif self.inKJV == 1 : 
      self.KJV += data
    elif self.inStrongs == 1 :
      # Do nothing. We already have the strongs number from the entry tag
      x = 0
    elif self.inEntry == 1 : 
      self.entry_text += data

#Escape function for SQL
def escape(str):
    return str.replace("'", "''").replace("\r", "").replace("\n","")
    
#Setup the database
db = pg.DB(dbname='ministry', host='localhost', user='www', passwd='your-pwd-here')

# Open the Strongs XML file
file = urllib.urlopen("strongsgreek.xml")
dataStr = file.read()

# Cleanup the data
dataStr = dataStr.replace('\n', '')

# Parse the XML
myparser = MyParser()
myparser.parse(dataStr)

print "Done."

