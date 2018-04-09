

from subprocess import call
import sys
import os
import fnmatch

# Expects files to be in `archive.zip`

if (len(sys.argv)<=1):
    exit("Usage:\nPass in path to Google's archive.zip file as argument.\nOn MacOS, this will typically be ~/Downlaods/archive.zip")

zip_file = sys.argv[1]
temp_dir = "/tmp"

# Extract .po files from zip
# eg: unzip "/Users/stan/Downloads/archive (8).zip" -d /tmp
call(["unzip", "-o", zip_file, "-d", temp_dir])

extract_dir = os.path.join(temp_dir, "archive")

po_files = []
for root, dirnames, filenames in os.walk(extract_dir):
    for filename in fnmatch.filter(filenames, '*.po'):
        pathname = os.path.join(root, filename)

        # Get language code
        try:
            language_code = pathname.split("/")[3] # Brittle
        except:
            continue

        print("Language: %s" % (language_code))

        dest_po_file =  os.path.join(".", language_code, "LC_MESSAGES", "messages.po")

        print("  %s\n  --> %s" % (pathname, dest_po_file))

        call(["cp", pathname, dest_po_file])
