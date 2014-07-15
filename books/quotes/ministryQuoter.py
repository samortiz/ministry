# Find a quote
import os, random, re, time, sys, traceback
from datetime import datetime

# https://github.com/sixohsix/twitter
from twitter import *

# Constants
QUOTES_USED_FILE = 'quotes_used.txt'
DATA_DIR = 'select_quotes'
STATE_FILE = 'ministryquoter.state'

# Twitter Credentials
CONSUMER_KEY='8P19bGTlvNDWollpb0pwX64LK'
CONSUMER_SECRET='OD5aPl9mb8VLETmQzmC2cg9VSGYktpOqboUfNID6fj5mnpflIE'

# Variables
allBooks = os.listdir(DATA_DIR)
allBooks.sort()
usedQuotes = []


def randomElement(aList) :
  'Returns one item from the list randomly'
  return aList[random.randrange(1, len(aList))]


def getRandomQuote(book):
  'Find the next available quote in the book'
  global DATA_DIR
  quoteFile = DATA_DIR+"/"+book
  quotesInBook = []
  with open(quoteFile) as f :
    quotesInBook = f.readlines()
  return randomElement(quotesInBook)


def clean(tweet):
  return tweet.strip()


def tweet(twitter, tweet):
  cleanTweet = clean(tweet)
  if (len(cleanTweet) > 10) and (len(cleanTweet) <= 140):
    print str(datetime.now())+" "+str(len(cleanTweet))+" chars  '"+cleanTweet+"'"
    twitter.statuses.update(status=cleanTweet)
  

# ------------------ Begin Main Program ----------------------

# Get all the quotes already used
if os.path.exists(QUOTES_USED_FILE):
  with open(QUOTES_USED_FILE, 'r') as f :
    usedQuotes = f.readlines()


#print "Authenticating with Twitter..."
MY_TWITTER_CREDS = os.path.expanduser('ministryquoter_credentials')
# Credentials do not already exist
if not os.path.exists(MY_TWITTER_CREDS):
  oauth_dance( "Ministry Quoter"
             , CONSUMER_KEY
             , CONSUMER_SECRET
             , MY_TWITTER_CREDS)


#Get book and quote
currentBook = ""
currentLine = 0
if not os.path.exists(STATE_FILE):
  currentBook = allBooks[0]
  currentLine = 0
else :
  with open(STATE_FILE, 'r') as f:
    currentBook = f.readline().strip()
    currentLine = int(f.readline().strip())    
    currentLine += 1

currentQuote = ""
storedQuote = "~"


# Authentication
#oauth_token, oauth_secret = read_token_file(MY_TWITTER_CREDS)
#twitter = Twitter(auth=OAuth(oauth_token, oauth_secret, CONSUMER_KEY, CONSUMER_SECRET))

# Find a unique random quote (NOT USED)
#while (storedQuote == "~") or (storedQuote in usedQuotes):
  #currentBook = randomElement(allBooks) 
  #currentQuote = getRandomQuote(currentBook) 
  #storedQuote = currentBook+"~"+currentQuote

# Find the next quote
quotesInBook = []
with open(DATA_DIR+"/"+currentBook) as f :
  quotesInBook = f.readlines()

# We are at the last quote in the book
if len(quotesInBook) <= currentLine:
  bookIndex = allBooks.index(currentBook)
  if len(allBooks) <= bookIndex+1 :
    print "Out of Books! Need more quotes in "+DATA_DIR
    print "Also remember to reset the state, or remove the already processed books"
  currentBook = allBooks[bookIndex+1]
  currentLine = 0
  with open(DATA_DIR+"/"+currentBook) as f :
    quotesInBook = f.readlines()
  bookDisplay = currentBook[:-4]
  print "Reading "+bookDisplay
  #tweet(twitter, "Reading "+currentBook)

#Get the quote
currentQuote = quotesInBook[currentLine]
storedQuote = currentBook+"~"+currentQuote

#tweet(twitter, currentQuote)
print storedQuote

if storedQuote != "~" :
  #Save the state
  with open(STATE_FILE, 'w') as f:
    f.write(currentBook+"\n")
    f.write(str(currentLine)+"\n")

  #Save quote to the file
  usedQuotes.append(storedQuote)
  with open(QUOTES_USED_FILE, 'a') as f:
    f.write(storedQuote)

