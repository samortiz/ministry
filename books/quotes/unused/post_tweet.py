# Quote machine
# https://github.com/sixohsix/twitter

import os
from twitter import * 

CONSUMER_KEY='8P19bGTlvNDWollpb0pwX64LK'
CONSUMER_SECRET='OD5aPl9mb8VLETmQzmC2cg9VSGYktpOqboUfNID6fj5mnpflIE'

print "Authenticating"

print "Debug Code, do no run"
exit()

MY_TWITTER_CREDS = os.path.expanduser('ministryquoter_credentials')
# Credentials do not already exist
if not os.path.exists(MY_TWITTER_CREDS):
  oauth_dance( "Ministry Quoter" 
             , CONSUMER_KEY
             , CONSUMER_SECRET
             , MY_TWITTER_CREDS)
# Regular Authentication
oauth_token, oauth_secret = read_token_file(MY_TWITTER_CREDS)
twitter = Twitter(auth=OAuth(oauth_token, oauth_secret, CONSUMER_KEY, CONSUMER_SECRET))

# Post a tweet
twitter.statuses.update(status='')


