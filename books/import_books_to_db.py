# Get chapters for books from the web
import sgmllib, os, re
from db_functions import *
from book_functions import *
from HTMLParser import HTMLParser

#File Variables
chapDir = 'chap_html'
cleanDir = 'clean_html'



# ---------------------- Misc Functions --------------------------------
def getAttr(attrName, attrs):
  "This will get an attribute from a list of (name,value) pairs, empty string if not found"
  for name,value in attrs:
    if name.lower().strip() == attrName.lower().strip():
      return value.lower().strip()
  return ""


def attrsToString(attrs):
  "Prints all the attrs to a string html-style"
  retVal = ""
  for name,value in attrs:
    retVal += " "+name.lower().strip()+"='"+value.lower().strip()+"'"
  return retVal


def breakingTag(tag):
  """Returns true if we should start a new chunk for this tag
   False means that the tag should be inline in the paragraph"""
  return (tag == "p" or tag == "div" or tag == "h1" or tag == "h2" or \
         tag == "li" or tag == "table" or tag == "td" or tag == "th" or tag == "tr" or \
         tag == "ol" or tag == "ul" )

# ---------------- Main HTML Parser -------------------------

class MyHTMLParser(HTMLParser):
  # Internal variables
  inGreek = False
  inHebrew = False
  inDoubleQuote = False

  chunks = []
  chunk = ""  
  tagName = ""
  tagClass = ""
  tagAttrs = []

  currTagName = ""
  currTagClass = ""
  currTagAttrs = []

  def storeChunk(self):
    if len(self.chunk) > 0:
      #print "  storing "+self.tagName+" "+self.tagClass+" : "+self.chunk
      self.chunks.append((self.tagName, self.tagClass, self.chunk, self.tagAttrs))
      self.chunk = ""
      self.tagName = ""
      self.tagClass = ""
      self.tagAttrs = []
      self.currTagName = ""
      self.currTagClass = ""
      self.currTagAttrs = []


  def handle_starttag(self, tag, attrs):
    # for all tags (breaking and non)
    self.currTagName = tag
    self.currTagClass = getAttr("class", attrs)
    self.currTagAttrs = attrs
    if self.currTagClass == "greek":
      self.inGreek = True 
    if self.currTagClass == "hebrew":
      self.inHebrew = True

    if breakingTag(tag):
      # If we're breaking, store the previous tag (if there is any)
      self.storeChunk()
      self.tagName = tag
      self.tagClass = getAttr("class", attrs)
      self.tagAttrs = attrs
      #print "start tag %s" % tag
    else: # We're not breaking, handling an inline tag
      # remove <br> tags in headers (h1, h2, h3)
      if not (self.currTagName == "br" and (self.tagName == "h1" or self.tagName == "h2" or self.tagName == "h3" \
              or self.tagName == "li") ):
        # it's a non-breaking tag, so we need to re-insert the tag data
        if len(self.chunk) > 0: self.chunk += " "
        self.chunk += "<"+self.currTagName+attrsToString(self.currTagAttrs)+">" # self.get_starttag_text()


  def handle_endtag(self, tag):
    if breakingTag(tag):
      #print "end %s" % tag
      self.storeChunk()
    else:
      # don't close br tags!
      if tag != "br": 
        #ending a non-breaking tag, so we need to insert the eng-tag
        self.chunk += "</"+tag+">"

    # exiting any tag will end the greek/hebrew tag (no nesting for me)  
    self.inGreek = False
    self.inHebrew = False
    self.inDoubleQuote = False


  def handle_data(self, data):
    newData = data.strip()
    # Determine whether to add a space before the chunk 
    # this handles cases like: "People's"  "Thomas' side"  "believers' life" 
    # This also handles double quotes eg. ~Sam said "here we go"~  ~People's "enjoyment"~
    if not (\
               self.chunk == "" \
            or self.chunk.endswith(">") \
            or (self.chunk.endswith('"') and self.inDoubleQuote) \
            or (newData == '"' and self.inDoubleQuote) \
            or newData == "'"  \
            or (self.chunk.endswith("'") and (newData.lower().startswith("s ") \
                  or newData.lower().startswith("s.") or newData.lower() == "s"))
       ): 
      self.chunk = self.chunk + " "
    self.chunk += newData 

    # Toggle the inDoubleQuote status on a double quote
    if newData == '"':
      if self.inDoubleQuote: self.inDoubleQuote = False
      else : self.inDoubleQuote = True


  def handle_charref(self, name):
    if name == "151": self.handle_data("-")
    elif name == "145": self.handle_data("'")
    elif name == "146": self.handle_data("'")
    elif name == "147": self.handle_data('"')
    elif name == "148": self.handle_data('"')
    elif name == "233": self.handle_data('e') #e with a funny accent
    elif name == "252": self.handle_data('u') # u with two dots
    elif name == "231": self.handle_data('c') # c with a hook
    elif name == "232": self.handle_data('e') # e with accent
    elif name == "133": self.handle_data('...')
    elif name == "150": self.handle_data('-')
    elif name == "227": self.handle_data('a') # a with squiggly over it
    elif name == "215": self.handle_data('x')
    elif name == "224": self.handle_data('a') # a with down accent
    elif name == "225": self.handle_data('a') # a with up accent
    elif name == "226": self.handle_data('a') # a with a cap
    elif name == "135": self.handle_data("+") #double dagger
    elif name == "189": self.handle_data("1/2")
    elif name == "169": self.handle_data("(c)") # copyright  
    elif name == "237": self.handle_data("i") # i accute
    elif name == "225": self.handle_data("a") # a accent  
    elif name == "239": self.handle_data("i") # i with two dots  

    elif self.inGreek or self.inHebrew :
      self.handle_data("&#"+name+";")
    else: 
      print "Error! Unhandled Char : "+name
      sys.exit # A Syntax error, so it will exit! :) 

    
  def handle_entityref(self, name):
    if name == "ldquo": self.handle_data('"')
    elif name == "rdquo": self.handle_data('"')
    elif name == "rsquo": self.handle_data("'")
    elif name == "lsquo": self.handle_data("'")
    elif name == "quot": self.handle_data('"')
    elif name == "mdash": self.handle_data("-")
    elif name == "nbsp": self.handle_data(" ")
    elif name == "amp": self.handle_data("&")
    elif name == "ndash": self.handle_data("-")
    elif name == "uuml": self.handle_data("u") # u with two dots
    elif name == "c.": self.handle_data("etc.")
    elif self.inGreek or self.inHebrew:
      self.handle_data("&"+name+";")
    else:
      print "Error! Unhandled Entity : "+name
      sys.exit # A syntax error, so it will exit :)


  def getChunks(self):
    self.storeChunk() # If there is one last chunk not yet dumped to the array
    return self.chunks

  
  def clearChunks(self):
    self.chunks = []


#----------------------------------------------------------------------------------------------
# Start the main program

# Directory containing all the books
currentBooks = os.listdir(cleanDir)
currentBooks.sort()

# remove from currentBooks all the books in the database
dbBooks = db.query("select name from book order by id").getresult()
for row in dbBooks:
  name = row[0]
  if (name in currentBooks):
    currentBooks.remove(name)

# DEBUG
#currentBooks = currentBooks[0:10]

# Go through all the books not in the database
for book in currentBooks:
  print "\n---------------------------------------------------------------------------------------------"
  print "Processing "+book
 
  # Store the book in the db
  displayName = bookDisplayName(book)
  db.query("insert into book(name, display_name) values ('"+escape(book)+"', '"+escape(displayName)+"')")
  book_id = dbGetOne("select id from book where name='"+escape(book)+"'")

  #Go through each page of HTML
  cleanFiles = os.listdir(os.path.join(cleanDir, book))
  cleanFiles.sort()
  for cleanFile in cleanFiles:
    cleanHtml = readFile(os.path.join(cleanDir, book, cleanFile))
    # cast pageNum to an int, as it has to be an int for the db
    pageNum = toInt(cleanFile[5:8])    

    # For the first page of each book, check to see if the toc file exists 
    if (cleanFile == "page_001.html"):
      tocFile = os.path.join(chapDir, book, "toc_with_links.html")
      if (os.path.exists(tocFile)):
        # If a toc file exists, we will use that to get the chapter information for the book
        cleanHtml = readFile(tocFile)
        print "Got toc!"
       
    #Get the paragraph chunks from cleanHtml
    print cleanFile
    parser = MyHTMLParser()
    parser.clearChunks()
    parser.feed(cleanHtml)
    chunks = parser.getChunks()
  

    #Store the chunks in book_chunks
    for chunk in chunks:
      print chunk[0]+" "+chunk[1]+" : "+chunk[2][:40]+" ... "+chunk[2][len(chunk)-40:]+" "+str(chunk[3])
      #print chunk[0]+"~"+chunk[1]+"~"+chunk[2]+"~"+str(chunk[3])+"\n"
      db.query("insert into book_chunk(book_id, page_num, tag_name, tag_class, data) values "+
       " ('"+book_id+"', "+str(pageNum)+", '"+escape(chunk[0])+"', '"+escape(chunk[1])+"', '"+escape(chunk[2])+"')") 
      book_chunk_id = dbGetOne("select id from book_chunk where book_id='"+book_id+"' and data='"+escape(chunk[2])+"' ")

      #Store the attributes
      for name,value in chunk[3]:
        if name == None: name = ""
        if value == None: value = ""
        if name != "class": 
          db.query("insert into book_chunk_attr (book_chunk_id, name, value) values "+
                   "('"+book_chunk_id+"', '"+escape(name.lower().strip())+"', '"+escape(value.lower().strip())+"')")


