#!/usr/local/bin/python

# Find all po files, and copy them to specified directory.
# Useful for uploading to Google Translator tool
#
# e.g.
# python copy_po_files_to_dir.py /tmp

import fnmatch
import os
from shutil import copyfile
import sys

from time import strftime

add_date = True

po_files = []
for root, dirnames, filenames in os.walk('.'):
    for filename in fnmatch.filter(filenames, '*.po'):
        pathname = os.path.join(root, filename)

        # Get language code
        try:
            language_code = pathname.split("/")[1]
        except BaseException:
            continue

        if add_date:
            iso_date = strftime("%Y%m%dT%H%M%S")
            new_file_name = "%s_%s_%s" % (language_code, iso_date, filename)
        else:
            new_file_name = "%s_%s" % (language_code, filename)

        destination_dir = sys.argv[1]
        new_pathname = os.path.join(destination_dir, new_file_name)

        copyfile(pathname, new_pathname)
        print "%s --> %s" % (pathname, new_pathname)
