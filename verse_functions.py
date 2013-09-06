#Functions for manipulating verse references
import pg, re
from db_functions import *

def getVerseId(ref) :
  return dbGetOne("select id from verse where ref='"+ref+"'")

def validRef(ref):
  "Returns true if the reference is valid syntax, for a single verse OR a range of verses, false if it is not valid syntax."
  if re.match("^((1 Chron)|(1 Cor)|(1 John)|(1 Kings)|(1 Pet)|(1 Sam)|(1 Thes)|(1 Tim)|(2 Chron)|"+
     "(2 Cor)|(2 John)|(2 Kings)|(2 Pet)|(2 Sam)|(2 Thes)|(2 Tim)|(3 John)|(Acts)|(Amos)|(Col)|(Dan)|(Deut)|(Eccl)|"+
     "(Eph)|(Esth)|(Exo)|(Ezek)|(Ezra)|(Gal)|(Gen)|(Hab)|(Hag)|(Heb)|(Hosea)|(Isa)|(James)|(Jer)|(Job)|(Joel)|(John)|(Jonah)|"+
     "(Josh)|(Jude)|(Judg)|(Lam)|(Lev)|(Luke)|(Mal)|(Mark)|(Matt)|(Micah)|(Nahum)|(Neh)|(Num)|(Obad)|(Phil)|(Philem)|(Prov)|"+
     "(Psa)|(Rev)|(Rom)|(Ruth)|(SS)|(Titus)|(Zech)|(Zeph)) [0-9]{1,3}[:]{0,1}(([0-9]{0,3})|()|(Title))"+
     "(([ ]{0,1}-[ ]{0,1}[0-9]{0,3}[:]{0,1}[0-9]{1,3})|())$", ref):
    return 1
  else : 
    return 0

def validRefSingle(ref): 
  "Returns true if the references is valid syntax for a single verse reference (not a range of verses) "
  if re.match("^((1 Chron)|(1 Cor)|(1 John)|(1 Kings)|(1 Pet)|(1 Sam)|(1 Thes)|(1 Tim)|(2 Chron)|"+
     "(2 Cor)|(2 John)|(2 Kings)|(2 Pet)|(2 Sam)|(2 Thes)|(2 Tim)|(3 John)|(Acts)|(Amos)|(Col)|(Dan)|(Deut)|(Eccl)|"+
     "(Eph)|(Esth)|(Exo)|(Ezek)|(Ezra)|(Gal)|(Gen)|(Hab)|(Hag)|(Heb)|(Hosea)|(Isa)|(James)|(Jer)|(Job)|(Joel)|(John)|(Jonah)|"+
     "(Josh)|(Jude)|(Judg)|(Lam)|(Lev)|(Luke)|(Mal)|(Mark)|(Matt)|(Micah)|(Nahum)|(Neh)|(Num)|(Obad)|(Phil)|(Philem)|(Prov)|"+
     "(Psa)|(Rev)|(Rom)|(Ruth)|(SS)|(Titus)|(Zech)|(Zeph)) [0-9]{0,3}[:]{0,1}(([0-9]{0,3})|()|(Title))$", ref):
    return 1
  else:
    return 0


def fixBookName(book_name):
  "Adjusts the book name to a normalized standard (same as cross ref in the Recovery Version)"
  book = book_name.strip().lower()
  
  #Fix up the book numbers
  book = book.replace("first", "1").replace("second","2").replace("third","3")
  # Remove the number (add it back later)
  bookNum = ""
  numMatch = re.match("^([1-3]) *(.*)$", book)
  if numMatch:
    bookNum = numMatch.group(1)
    book = numMatch.group(2) #Remove the book number

  if (book=="genesis"): book="gen"
  if (book=="exodus"): book="exo"
  if (book=="leviticus"): book="lev"
  if ((book=="numbers") | (book=="number")): book="num"
  if ((book=="deuteronomy") | (book=="deu") | (book=="due") | (book=="duet")): book="deut"
  if ((book=="joshua") | (book=="jos")): book="josh"
  if ((book=="judges") | (book=="jdg")): book="judg"
  if ((book=="ruth") | (book=="rut")): book="ruth"
  if ((book=="samuel") | (book=="sa")): book="sam"
  if ((book=="ki") | (book=="king")): book="kings"
  if ((book=="chronicles") | (book=="chr") | (book=="ch")): book="chron"
  if (book=="ezr"): book="ezra"
  if (book=="nehemiah"): book="neh"
  if ((book=="esther") | (book=="est")): book="esth"
  if (book=="jb"): book="job"
  if ((book=="psalms") | (book=="psalm")): book="psa"
  if ((book=="proverbs") | (book=="prv")): book="prov"
  if ((book=="ccclesiastes") | (book=="ecc")): book="eccl"
  if ((book=="sos") | (book=="song of songs") | (book=="song of solomon")): book="ss"
  if (book=="isaiah"): book="isa"
  if (book=="jeremiah"): book="jer"
  if (book=="lamentations"): book="lam"
  if ((book=="ezekiel") | (book=="ezk")): book="ezek"
  if (book=="daniel"): book="dan"
  if (book=="hos"): book="hosea"
  if (book=="joe"): book="joel"
  if ((book=="am") | (book=="amo")): book="amos"
  if ((book=="ob") | (book=="oba")): book="obad"
  if (book=="jon"): book="jonah"
  if (book=="mic"): book="micah"
  if (book=="nah"): book="nahum"
  if ((book=="habakkuk") | (book=="habbakuk") | (book=="habakuk")): book="hab"
  if ((book=="zephaniah") | (book=="zep")): book="zeph"
  if (book=="haggai"): book="hag"
  if ((book=="zechariah") | (book=="zachariah") | (book=="zec")): book="zech"
  if (book=="malachi"): book="mal"
  if ((book=="mat") | (book=="mathew") | (book=="matthew")): book="matt"
  if ((book=="mk") | (book=="mrk")): book="mark"
  if ((book=="lk") | (book=="luk")): book="luke"
  if ((book=="jn") | (book=="jo") | (book=="joh")): book="john"
  if (book=="act"): book="acts"
  if (book=="romans"): book="rom"
  if ((book=="corinthians") | (book=="corinthian") | (book=="co")): book="cor"
  if ((book=="galatians")|(book=="galatian")|(book=="galations")|(book=="galation")|(book=="ga")) : book="gal"
  if (book=="ephesians"): book="eph"
  if ((book=="philipians") | (book=="phillipians") | (book=="philippians") | (book=="phi")): book="phil"
  if ((book=="colosians")|(book=="colossians")): book="col"
  if ((book=="thessalonians") | (book=="thess") | (book=="thesalonians") | (book=="th")): book="thes"
  if ((book=="timothy") | (book=="ti")): book="tim"
  if (book=="tit"): book="titus"
  if (book=="phm"): book="philem"
  if (book=="hebrews"): book="heb"
  if (book=="jam"): book="james"
  if ((book=="peter") | (book=="pe")): book="pet"
  if ((book=="jd") | (book=="jud")): book="jude"
  if ((book=="revelation") | (book=="revelations")): book="rev"

  # Initcap the book name
  book = (book[0] .upper()+ book[1:])
  if (book == "Ss"): book = "SS" #Exception to the initcap rule
  
  #Add back the book number (removed for easier processing)
  if bookNum != "":
    book = bookNum+" "+book

  return book
#end function fixBookName


def fixRef(ref_orig) :
  "This will try to convert a reference into a valid one, if possible.  It will return the valid reference, or empty string if it fails to fix it."
  # if it's valid, that's good enough, don't need to do anything else
  if (validRef(ref_orig)): return ref_orig
  # Try some translations on the reference
  ref = ref_orig.strip().lower()

  #Pull all the pieces of the string out 
  match = re.match("^([123]{0,1})[ ]*([ a-z\.]{1,20})[ ]*([0-9]{0,3})[ ]*([:;]{0,1})[ ]*(([0-9]{0,3})|(title))"+
      "(([ ]*-[ ]*((([0-9]{1,3})[ ]*[:;])|())[ ]*([0-9]{1,3}))|())$", ref)

  if (not match): return "" # Totally invalid reference, we cannot even try to fix it up
  bookNum = str(match.group(1))
  book = str(match.group(2)).replace(".","").strip()
  chap = str(match.group(3)) # This will contain the chapter, but if there is no colon in the string, it will contain the verse (eg Jude 13)
  colon = str(match.group(4)).replace(";",":")
  verse = str(match.group(5))
  endChap = str(match.group(12))
  endVerse = str(match.group(14))

  # Fix up the book name (shorten full book names, fix mis-spelling, wrong abbreviations, etc)
  book = fixBookName(book)

  # Special case for Psalm Titles (not really a verse, but where else to put it?)
  if (verse == "title"): verse = verse[0].upper()+verse[1:]

  #Construct the new (and hopefully valid) reference from the pieces
  newRef = ""
  if ((bookNum != "") & (bookNum != "None")): newRef += bookNum+" "
  newRef += book+" "
  if ((chap != "") & (chap != "None")): newRef += chap
  if ((colon != "") & (colon != "None")): newRef += ":"
  newRef += verse
  if ((endVerse != "") & (endVerse != "None")): 
    newRef += "-"
    if ((endChap != "") & (endChap != "None")): newRef += endChap+":"
    newRef += endVerse

  #print "\nfixed reference '"+ref_orig+"' to '"+newRef+"'"
  #print "num="+bookNum+" book="+book+" chap="+chap+" verse="+verse+" endChap="+endChap+" endVerse="+endVerse+" newRef="+newRef
  #print  (" 1="+str(match.group(1))+" 2="+str(match.group(2))+" 3="+str(match.group(3))+" 4="+str(match.group(4))+" 5="+str(match.group(5))+
  #" 6="+str(match.group(6))+" 7="+str(match.group(7))+" 8="+str(match.group(8))+" 9="+str(match.group(9))+" 10="+str(match.group(10))+" 11="+str(match.group(11))+
  #" 12="+str(match.group(12))+" 13="+str(match.group(13))+" 14="+str(match.group(14))+" 15="+str(match.group(15)))+" \n"
  return newRef
