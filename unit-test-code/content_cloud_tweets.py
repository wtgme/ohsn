#!/usr/bin/env python

""" 
tags_from_tweets.py - Take hashtags from tweets in SQLite database. Output to text file.

"""

import sys
import re
import sqlite3

def main():
    """Main function."""   
    database = "test-database.sqlite"
    conn = sqlite3.connect(database)
    c = conn.cursor()
    c.execute('SELECT * FROM user_tweets')  
    tweets = c.fetchall() 
    
    # CREATE EMPTY DICTIONARY FOR TAGS    
    all_text = []

    for row in tweets:
        id = row[0]
        content = row[16] #the content
        if content:       
            #print(content.decode('unicode_escape').encode('ascii','ignore'))
            tags = content.lower() 
            #print content
        else:
            tags = ''
        tags = re.sub('\n', ' ', tags)
        
        # to remove 'u' before each tweet in the list --> DOESN'T WORK WITH SQLITE INSERTION
        tags = tags.encode("utf-8")                  
            
        all_text.append(tags)                  

        print "\radding content for id: %d" % id,
        sys.stdout.flush()
 
    all_hashtags = ' '.join(all_text)
    out=file('all_text_Content.txt','w')
    out.write(all_hashtags)     
   
if __name__ == "__main__":
    main()