#!/usr/bin/env python
# This script goes through the HTML files of the bible and stores the footnote text in a postgres database
import urllib, sgmllib,pg, re
from verse_functions import *

class MyParser(sgmllib.SGMLParser):

    def parse(self, s, book):
        self.book = book
        self.feed(s)
        self.close()

    def __init__(self, verbose=0):
        "Initialize an object, passing 'verbose' to the superclass."
        sgmllib.SGMLParser.__init__(self, verbose)
        self.notes = []
        self.inP = 0
        self.inS = 0
        self.inU = 0
        self.inIgnore = 0
        self.clearVars()

    def clearVars(self):
        self.currState = "" # Where we are in the parsing of this note
        self.currRef = "" # The reference for the current verse
        self.currNum = "" # The footnote number (1,2,3...)
        self.currLetter = "" # The cross reference letter (a,b,c..)
        self.currWord = "" # The word referenced by the cross reference or footnote eg. "Egypt"
        self.crossRef = "" # Cross ref  verse reference "John 1:21"
        self.currPar = "" # Foonote paragraph num (1,2,3...)
        self.currNote = "" # Footnote text


    def addCurrNote(self):
      "This will insert the current note into the database"
      self.crossRef = self.crossRef.strip()
      self.currNote = self.currNote.strip()
       
      #Setup the number and letter
      match = re.match("^([0-9]*)([a-z]*)$",  self.currNum.lower().strip())
      if (match):
        self.currNum = str(match.group(1))
        self.currLetter = str(match.group(2))
      
      fixedRef = fixRef(self.currRef)
      if (fixedRef == ""): 
        print "ERROR! '"+self.currRef+"' is not a valid reference"
        return
      self.currRef = fixedRef
      verse_id = getVerseId(self.currRef)
      if (verse_id == ""): 
        print "ERROR! Could not get verse for ref "+self.currRef
        return
      
      #Insert the footnote into the database
      if ((len(self.currNote) > 0) and (self.currNum != "")): 
        db.query("insert into verse_note (verse_id, num, word, par, note) values "+
                 "("+verse_id+", '"+self.currNum+"', '"+escape(self.currWord)+"', '"+self.currPar+"', '"+escape(self.currNote)+"')")
     
      print ("AddNote : ref="+self.currRef+"#"+verse_id+" num="+self.currNum+" l="+self.currLetter+
          " par="+self.currPar+" word="+self.currWord+" cross="+self.crossRef+"\ncurrNote="+self.currNote)
      
# Convert the cross references to verse ids and insert them
#      if (self.crossRef != ""): 
#        for crossRef in self.crossRef.split(";"):
#          print "Processing ref : "+crossRef
#          fixedCrossRef = fixRef(crossRef)
#          if (fixedCrossRef == ""): 
#            print "ERROR! cross reference '"+crossRef+"' is not a valid reference in verse "+self.currRef
#            continue
#          crossRef_verse_id = getVerseId(fixedCrossRef)
#          if (crossRef_verse_id == ""):
#            print "ERROR! Could not find verse id for fixed cross ref "+fixedCrossRef+" in verse " +self.currRef
#            continue
#          if (self.currLetter != ""):
#            db.query("insert into crossref (verse_id, letter, word, ref_verse_id) values "+
#                     "("+verse_id+", '"+self.currLetter+"', '"+escape(self.currWord)+"', "+crossRef_verse_id+") ")


    # s tags are superscripts for cross-references and footnotes
    def  start_s(self, attributes):
        self.inS = 1
    def end_s(self):
        self.inS = 0

    def  start_u(self, attributes):
        self.inI = 1
    def end_u(self):
        self.inU = 0

    def  start_p(self, attributes):
        self.inP = 1
        self.currNote = ""
        self.currState = "ref"
        print "start P"
        
    def end_p(self):
        self.inP = 0
        #Insert the current footnote into the database
        self.addCurrNote()
        # We're done the note, so reset all the variables
        self.clearVars()

    def start_br(self, attributes):
      if (self.currState == "paragraph_note"): 
        self.addCurrNote()
        self.currNote = "" # Reset the note
        #After this the state will be set to note (below line), so it can start the next paragraph (if necessary)
        
      if (self.currState != ""): self.currState = "note"
      print "BR"

    # Check whether we are in an h1,h2, h3, h4 tag, these are chapter headings
    def start_small(self, attributes): #A small tag is used in the footer, the data should be ignored
        self.inIgnore = 1
    def end_small(self):
        self.inIgnore = 0
    def start_span(self, attributes):
        self.inIgnore = 1
    def end_span(self):
        self.inIgnore = 0   
    def start_ins(self, attributes):
        self.inIgnore = 1
    def end_ins(self):
        self.inIgnore = 0   
    def start_del(self, attributes):
        self.inIgnore = 1
    def end_del(self):
        self.inIgnore = 0   
    def start_pre(self, attributes):
        self.inIgnore = 1
    def end_pre(self):
        self.inIgnore = 0  
    def start_var(self, attributes):
        self.inIgnore = 1
    def end_var(self):
        self.inIgnore = 0  
    def start_code(self, attributes):
        self.inIgnore = 1
    def end_code(self):
        self.inIgnore = 0  


    def handle_data(self, data):
        "Handle the text within tags"
        print "state="+self.currState+" p="+`self.inP`+" s="+`self.inS`+" u="+`self.inU` +" i="+`self.inIgnore`+" data="+data

        if (self.currState == "ref"):
          self.currRef = data.strip()
          self.currState = "num"
          
        elif (self.currState == "num"): 
          self.currNum = data.strip()
          self.currState = "word"
          
        elif (self.currState == "word"):
          self.currWord = data.strip()
          self.currState = "crossref"
          
        elif (self.currState == "crossref"):
          if (data == ";"): self.crossRef += "; "
          else: self.crossRef += data.strip()
          
        elif (self.currState == "note"): 
          # If it's a number in a superscript, it's a reference to a footnote, so modify it
          if ((self.inS == 1) and (re.match("^[0-9]{1,2}$", data.strip()))): 
            self.currNote += "<sup>"+data+"</sup>"
          else: 
            self.currNote += data
            
          #Check to see if we're starting a paragraph-style note (then we need to split the footnote up by paragraphs)
          parMatch = re.match("^\[([0-9]{1,2})\]$", data.strip())
          if (parMatch): 
            paragraph = str(parMatch.group(1))
            self.currPar = paragraph
            self.currState = "paragraph_note"
            self.currNote = "" #Start again, throw away all the stuff before this
            
        
        #This will happen when the foonote has more than one paragraph
        elif (self.currState == "paragraph_note"):
          self.currNote += data
          
          
        


#Escape function for SQL
def escape(str):
    return str.replace("'", "''").replace("\r", "")
    
#Setup the database
db = pg.DB(dbname='ministry', host='localhost', user='www', passwd='your-pwd-here')

books = ("Gen","Exo","Lev","Num","Deu","Jos","Jdg","Rut","1Sa","2Sa","1Ki",
    "2Ki","1Ch","2Ch","Ezr","Neh","Est","Job","Psa","Prv","Ecc","SoS",
    "Isa","Jer","Lam","Ezk","Dan","Hos","Joe","Amo","Oba","Jon","Mic",
    "Nah","Hab","Zep","Hag","Zec","Mal","Mat","Mrk","Luk","Joh","Act",
    "Rom","1Co","2Co","Gal","Eph","Phi","Col","1Th","2Th","1Ti","2Ti",
    "Tit","Phm","Heb","Jam","1Pe","2Pe","1Jo","2Jo","3Jo","Jud","Rev")

# Open the HTML file
for book in books:
#for book in ("3Jo", "Joe" ) :
  print "Processing "+book+"..."
  file = urllib.urlopen("./notes/"+book+"N.htm")
  dataStr = file.read()

  #Replace some HTML sepecific characters
  dataStr = dataStr.replace("\n", "") 
  dataStr = dataStr.replace("&nbsp;", " ")
  dataStr = dataStr.replace("&mdash;", "-")
  dataStr = dataStr.replace("&bull;", "-")
  dataStr = dataStr.replace("&rsquo;", "'")
  dataStr = dataStr.replace("&hellip;", " ")
  dataStr = dataStr.replace("<q>", " ").replace("</q>", " ")
  
  
  # Parse the HTML
  myparser = MyParser()
  myparser.parse(dataStr, book)

# Final output
print "imported "+`len(books)`+" books"

  
