from subprocess import call

print("=========================================")
print("Extracting .po files from downloaded .zip")
print("=========================================")
call(["python", "extract_po_files_from_gtt_zip.py", "~/Downloads/archive.zip"])

print("==========================")
print("Fixing errors in .po files")
print("==========================")
call(["python", "fix_po_files.py"])


print("==========================")
print("Compiling to .mo files")
print("==========================")
call(["pybabel", "compile", "-f", "-d", "."])
