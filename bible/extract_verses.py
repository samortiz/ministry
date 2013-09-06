#!/usr/bin/env python
# This script goes through the HTML files of the bible and stores the verse text in a postgres database
import urllib, sgmllib,pg, re

class MyParser(sgmllib.SGMLParser):

    def parse(self, s, book):
        self.book = book
        self.feed(s)
        self.close()
        # Cleanup the last trailing verse
        self.addCurrVerse()

    def __init__(self, verbose=0):
        "Initialize an object, passing 'verbose' to the superclass."
        
        sgmllib.SGMLParser.__init__(self, verbose)
        self.book = ""
        self.verses = []
        self.currRef = ""
        self.currVerse = ""
        self.inS = 0
        self.inTT = 0
        self.inIgnore = 0
        self.inRef = 0
        self.inRefAnchor = 0
        self.inOutline = 0

    # s tags are superscripts for cross-references and footnotes
    def  start_s(self, attributes):
        self.inS = 1
    def end_s(self):
        self.inS = 0

    # tt tags are outlines
    def start_tt(self, attributes):
        self.inTT = 1
    def end_tt(self):
        self.inTT = 0

    # Check whether we are in an h1,h2, h3, h4 tag, these are chapter headings
    def start_h1(self, attributes):
        self.inIgnore = 1
    def end_h1(self):
        self.inIgnore = 0
    def start_h2(self, attributes):
        self.inIgnore = 1
    def end_h2(self):
        self.inIgnore = 0
    def start_h3(self, attributes):
        self.inIgnore = 1
    def end_h3(self):
        self.inIgnore = 0
    def start_h4(self, attributes):
        self.inIgnore = 1
    def end_h4(self):
        self.inIgnore = 0
    def start_h5(self, attributes):
        self.inIgnore = 1
    def end_h5(self):
        self.inIgnore = 0
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
        

    def start_u(self, attributes):
      for name, value in attributes:
        if (name=="class") & (value=="o") :
          self.inOutline = 1
    def end_u(self):
      self.inOutline = 0

    def start_a(self, attributes):
        # Check to see if the anchor tag, is a reference anchor (as opposed to a footnote, cross reference, other...)
        for name, value in attributes:
            if (name=="href") :
                if (value=="a.htm"):
                    self.inRefAnchor = 1
                else :
                    self.inRefAnchor = 0
            
    def end_a(self):
        self.inRefAnchor = 0
        
    def addCurrVerse(self):
        "Add a verse to the current list of verses, it must have a valid reference and some verse text." 
        
        if ((len(self.currRef.strip()) > 0) & (len(self.currVerse.strip()) > 0)) :
          ref = self.currRef.strip()
          verse = self.currVerse.strip()
          self.verses.append((ref, verse))
          #print ref +":"+verse
            
          # Concatenate the verses that were split by outlines into A and B portions 
          if (ref[-1] == "b") : #If this is the second half of a verse
            bVerse = self.verses[-1]
            aVerse = self.verses[-2]
            del self.verses[-2:] # Remove the last two entries (the a and b verses)
            ref = ref[0:-1] # Strip off the last character 
            verse = aVerse[1] + " " + bVerse[1]
            self.verses.append((ref, verse))
            #print "Concatenated "+ref+" : "+verse
        
    def handle_data(self, data):
        "Handle the text within tags"
        
        #print "s="+`self.inS`+" tt="+`self.inTT` +" i="+`self.inIgnore`+" data="+data
       
       # If we are not in a superscript (footnotes/cross-ref) or TT (outline) tag, or any ignored tag 
        if ((self.inS == 0) & (self.inTT == 0) & (self.inIgnore == 0) & (self.inOutline == 0)) :
            if  ((data == self.book) & (self.inRefAnchor == 1)): # The chunk matches the book title, and we are in a reference-style anchor tag 
                self.addCurrVerse() # Store the current verse
                self.inRef = 1 # The start of the reference is the book name
                self.currRef = "" # Begin a new reference
                self.currVerse = "" # Begin a new verse
            
            if (data == "-"):
                self.inRef = 0 # Start the verse text
                return # No further processing, don't append the data to any strings, throw away the - character
                
            # If we are in a reference, then build the reference string
            if (self.inRef == 1) :
                self.currRef = self.currRef + data
            else : # We are in a verse, so build the verse string
                self.currVerse = self.currVerse + data
    


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
for book in books: # ("3Jo", "Rev" ) :
  print "Processing "+book+"..."
  file = urllib.urlopen("./verses/"+book+".htm")
  dataStr = file.read()

  #Replace some HTML sepecific characters
  dataStr = dataStr.replace("\n", "") 
  dataStr = dataStr.replace("&nbsp;", " ")
  dataStr = dataStr.replace("&mdash;", "-")
  dataStr = dataStr.replace("&bull;", "-")
  dataStr = dataStr.replace("&rsquo;", "'")
  dataStr = dataStr.replace("<q>", " ").replace("</q>", " ")
  
  
  # Parse the HTML
  myparser = MyParser()
  myparser.parse(dataStr, book)

  for  verse in myparser.verses :
    #print verse[0]+" - "+verse[1]
    db.query("insert into verse (book, ref, verse) values "+
        "('"+book+"', '"+verse[0]+"', '"+escape(verse[1])+"') ")

# Final output
print "imported "+`len(books)`+" books"

  
