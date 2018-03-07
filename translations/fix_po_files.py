#!/usr/local/bin/python

# Script to fix or detect various issues that come up in po files

import fnmatch
import os
import re

po_files = []
for root, dirnames, filenames in os.walk('.'):
    for filename in fnmatch.filter(filenames, '*.po'):
        pathname = os.path.join(root, filename)

        # Get language code
        try:
            language_code = pathname.split("/")[1]
        except:
            continue

        print(language_code)

        f = open(pathname,"r+")
        d = f.readlines()
        f.seek(0)
        for line in d:

            # Fix spaces in closing tags (Google Translator Toolkit does this)
            (line, subs) = re.subn(r'</ +', '</', line, flags=re.IGNORECASE)
            if subs > 0:
                print ("-FIXED %s: `</ ` space" % language_code)

            if line == '"Language: \\n"\n':
                # Fix dumb issue  "Language:" header is present, but
                # Doesn't specify the language
                print ("-FIXED %s: `Langage: header`" % language_code)
                line = '"Language: %s\\n"\n' % language_code

            f.write(line)

        f.truncate()
        f.close()
