#!/usr/local/bin/python

# Script to fix dumb issue  "Language:" header is present, but
# Doesn't specify the language

import fnmatch
import os

po_files = []
for root, dirnames, filenames in os.walk('.'):
    for filename in fnmatch.filter(filenames, '*.po'):
        pathname = os.path.join(root, filename)

        # Get language code
        try:
            language_code = pathname.split("/")[1]
        except:
            continue

        print language_code

        # Fix it
        f = open(pathname,"r+")
        d = f.readlines()
        f.seek(0)
        for i in d:
            if i == '"Language: \\n"\n':
                print ("-FIXED %s" % language_code)
                f.write('"Language: %s\\n"\n' % language_code)
            else:
                f.write(i)
        f.truncate()
        f.close()
