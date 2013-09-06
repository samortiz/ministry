#!/usr/bin/env python
#This script goes through the HTML files for the hymns and stores the text in a postgres database
import urllib, sgmllib,pg, re

class MyParser(sgmllib.SGMLParser):
    "A simple parser class."

    def parse(self, s):
        "Parse the given string 's'."
        self.feed(s)
        self.close()

    def __init__(self, verbose=0):
        "Initialise an object, passing 'verbose' to the superclass."
        sgmllib.SGMLParser.__init__(self, verbose)
        self.lines = []
        self.inLine = 0
        self.indent = ""
        self.inItalics = 0
        self.currLine = ""
        self.currentVerse = ""
        self.author = ""
        self.composer = ""
        self.chinese_num = ""
        self.spanish_num = ""
        self.korean_num = ""
        self.tagalog_num = ""
        self.meter = ""
        self.inMetabox = 0
        self.lastData = ""

    def start_p(self, attributes):
        "Parse a line from the hymn, paragraph tags"
        for name, value in attributes:
            if ((name == "class") & ((value=="line") | (value=="line2") | (value=="line4") | (value=="line6") | (value=="line6") | (value=="line8") | 
                                     (value=="cline") | (value=="cline2") | (value=="cline4") | (value=="cline6") | 
                                     (value=="sline") | (value=="sline2") | (value=="sline4") | (value=="sline8")  )):
                self.inLine = 1
                self.currLine = "" # Clear any previous line, hopefully it is already inserted! 
                match = re.match("^[cs]{0,1}line([0-9])$", value)
                if (match): 
                  self.indent = str(match.group(1))
                else: 
                  self.indent = "0"
    
    def end_p(self):
        self.inLine = 0

    def start_i(self, attributes):
      self.inItalics = 1
    def end_i(self):
      self.inItalics = 0

    def start_div(self, attributes):
        "parse opening div tags" 
        for name, value in attributes:
            if (name=="class") & (value=="chorus"):
                self.currentVerse="c"
            elif (name=="class") & (value=="singleverse"):
                self.currentVerse="s"
            elif (name=="class") & (value=="metabox"):
                self.inMetabox = 1
    
    def end_div(self):
        self.inMetabox = 0     

    def handle_data(self, data):
        "Handle the text within tags"
        #If we are within a line of the song (p tag)
        if self.inLine == 1:
          #print "i="+`self.inItalics`+" currLine="+self.currLine+" data="+data
          if (self.inItalics == 1): self.currLine += data
          else: self.lines.append((self.currentVerse, self.currLine+data, self.indent))
         
        #Locate which verse we are on
        if re.match("^ [0-9]+ $", data):
            self.currentVerse = data.replace(" ", "")

        #Recognize Author and composer tags
        if self.inMetabox == 1 :
            if (data in ("E",  " C",  " K",  " S", " T", "Lyrics", "Music",  "Meter")):
                self.lastData = data
            elif ((data not in ("",  ":",  "From ")) & (self.lastData != "")) : 
                if (self.lastData == " C") : self.chinese_num = data
                if (self.lastData == " S") : self.spanish_num = data
                if (self.lastData == " K") : self.korean_num = data
                if (self.lastData == " T") : self.tagalog_num = data
                if (self.lastData == "Lyrics") : self.author = self.author+data
                if (self.lastData == "Music") : 
                    if (data[0:3] == "(2)" ) : self.composer = self.composer+" "+data
                    else : self.composer = self.composer+data
                if (self.lastData == "Meter") : self.meter = data
                
                # Clear the lastData, so you only get the single next item after the keyword data (music and lyrics sometimes have multiple lines)
                if (self.lastData not in ("Lyrics", "Music")) : self.lastData = "" 

    def get_lines(self):
        "Return the list of lines."
        return self.lines



#Escape function for SQL
def escape(str):
    return str.replace("'", "''").replace("\r", "").replace("\n","")
    
#Setup the database
db = pg.DB(dbname='ministry', host='localhost', user='www', passwd='your-pwd-here')

# Open the hymn htm file
for hymn in range(1,1349): # max 1352 (there are 1351 hymns, some added bonus ones above the hymn book's 1348)
#for hymn in range(1195,1199):
  file = urllib.urlopen("./hymns/"+`hymn`+".htm")
  dataStr = file.read()

  #Replace some funny characters
  dataStr = dataStr.replace("&nbsp;", " ")
  dataStr = dataStr.replace("&mdash;", "-")

  # Parse the HTML
  myparser = MyParser()
  myparser.parse(dataStr)

  # Insert the hymn into the database
#  db.query("insert into hymn (hnum, author, composer, chinese_num, spanish_num, korean_num, tagalog_num, meter) values "+
#       "("+`hymn`+", '"+escape(myparser.author)+"', '"+escape(myparser.composer)+"', '"+escape(myparser.chinese_num)+
#      "', '"+escape(myparser.spanish_num)+"', '"+escape(myparser.korean_num)+"', '"+escape(myparser.tagalog_num)+"', '"+escape(myparser.meter)+"'  )")
 

  #Progress feedback for the user
  print "Importing Hymn "+`hymn`

  # Setup to go through the lines
  lastStanza = "0"
  lineCounter = 1 # reset on each stanza
  lineOrder = 0 # Not reset for each stanza
 
  # Go through each line of the hymn
  for line in myparser.get_lines():
    #If we are moving on to a new stanza
    if (lastStanza != line[0]):
      lineCounter = 1
      lastStanza = line[0]
    else:
      lineCounter = lineCounter + 1
    
    lineOrder = lineOrder + 1
   
    # Insert the line into the database
    sql = ("insert into hymn_line (hnum, stanza, line, data, type, lineorder, indent) values "+
        "("+`hymn`+", '"+line[0]+"', "+`lineCounter`+", '"+escape(line[1])+"', 'data', "+str(lineOrder)+", "+line[2]+" ) ")
    print sql
    db.query(sql)

