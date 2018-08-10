import sys
import json
'''

Adaptation of someone elses code, this will save to file, so avoiding the need for pipes etc.

Orignial code was pilfered from:

https://github.com/chbrown/lexicons/blob/master/lexicons/liwc.py

Credit goes to:

https://github.com/chbrown


The LIWC .dic format looks like this:
%
1   funct
2   pronoun
%
a   1   10
abdomen*    146 147
about   1   16  17

pipe that file into this, get a json trie on stdout
'''

categories = {}
trie = {}

outfilename = 'liwc_2007.trie'
outfile = open(outfilename,"w")

infilename = 'LIWC2007B.txt'
infile = open(infilename,"r")

def add(key, categories):
    cursor = trie
    for letter in key:
        if letter == '*':
            cursor['*'] = categories
            break
        if letter not in cursor:
            cursor[letter] = {}
        cursor = cursor[letter]
    cursor['$'] = categories

for line in infile:
    print line
    line = unicode(line, errors='ignore')
    if not line.startswith('%'):
        parts = line.strip().split('\t')
        if parts[0].isdigit():
            # cache category names
            categories[parts[0]] = parts[1]
        else:
            # print parts[0], ':', parts[1:]
            add(parts[0], [categories[category_id] for category_id in parts[1:]])

# indent=4,

print "creating data string"
data_string = json.dumps(trie, sort_keys=True)
#data_string = json.dumps(trie, sort_keys=True)
print "wrinting to file"
outfile.write(data_string +'\n')
print "output written"
outfile.close()
infile.close()
