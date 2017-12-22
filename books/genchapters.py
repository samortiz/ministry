# Generate the chapter data files
import sgmllib
import os, random, time, re
from file_functions import *

#File Variables
chapDir = 'chap_html'
cleanDir = 'clean_html'
rawDir = 'raw_html'

#Data Variable
chapterData = []


# --------------------- Helper Functions ------------------------------------------------------

def getPageFileForChapter(book, chapNum):
  pageNum = ''
  allPages = os.listdir(os.path.join(rawDir, book))
  for page in allPages:
    if page.startswith('page_'):
      pageHtml = readFile(os.path.join(rawDir, book, page))
      page_search = re.search('Chapter <span class="secondary radius label">'+str(chapNum)+' of [0-9]+</span> Section <span class="secondary radius label">1 of [0-9]+</span></span>', pageHtml)
      if page_search:
        return page
  return 'Error could not find chapter '+str(chapNum)+' in book '+book;


#----------------------------------------------------------------------------------------------
# Start the main program

# Directory containing all the books downloaded so far
allBooks = os.listdir(rawDir)
missingBooks = []

for book in allBooks:
  if (not (    os.path.exists(os.path.join(chapDir, book)) # No folder created
           and (   os.path.exists(os.path.join(chapDir, book, "toc_with_links.html"))  # links done already 
                or len(os.listdir(os.path.join(chapDir, book))) == 1))):   # There is only one chapter (old format)
    missingBooks.append(book) 
 
#missingBooks = ['Christ and the Cross']  #DEBUG
print "Books Missing Chapters "+str(len(missingBooks))
print missingBooks  

for book in missingBooks:
  ensure_dir(os.path.join(chapDir, book))
  tocHtml = readFile(os.path.join(cleanDir, book, "page_001.html"))
  # Find all the <a tags
  links = re.findall('<a href=books.cfm\?cid\=[0-9A-F]+>', tocHtml)
  chapCount = 0; # Start at the first chapter
  for link in links:
    chapCount += 1;
    chapPage = getPageFileForChapter(book, chapCount);
    newLink = '<a href="'+chapPage+'">'
    tocHtml = tocHtml.replace(link, newLink)
  if len(links) > 0: 
    # Orig value    
    writeStringToFile(os.path.join(chapDir, book, "chapter_Table of Contents.html"), tocHtml)
    # New intro page    
    writeStringToFile(os.path.join(chapDir, book, "toc_with_links.html"), tocHtml)
  else:
    # One page book, no TOC
    writeStringToFile(os.path.join(chapDir, book, "page_001.html"), tocHtml)
  print "Found chapters for "+book
  






