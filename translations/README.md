# Localization

Localization is done with the [Flask-Babel](https://pythonhosted.org/Flask-Babel/) module.

Translated files live in `translations/<Language Code>/LC_MESSAGES/messages.po`.

## New English strings

Use this command to update strings after new or edited English strings. It will create a new `messages.pot` file.
```
pybabel update -i messages.pot -d translations
```

Then run  `merge_new_pot.sh` which will merge these new english phrases into all the language `.po` files, using the `msgmerge` command.

If you don't have `msmerge` you can get it on Mac with homebrew:
```
brew install gettext
brew link gettext --force
```

## New or updated translation files

After downloading or manual edits to `.po` files, you must compile translations:
```
pybabel compile -f -d  translations
```
(The `-f` flag is needed to force the compile, since downloads from Google translator are always marked as 'fuzzy')

If you get an error `ValueError: expected only letters, got u''`, run the python script `fix_po_files.py`. This error is caused by a `.po` file containg an empty language header: `"Language: \n"`, where it should be e.g. `"Language: de\n"`

This step will generate compiled `.mo` files from each `.po`.  These are the files used to actaully render translated versions of the site.

## New language

```
pybabel init -i messages.pot -d translations -l <Language Code>
```
See [pybabel docs for init](http://babel.pocoo.org/en/latest/cmdline.html#init)

## Fresh Start

Use this command to start from scratch, extracting strings into a file `messages.pot`
```
pybabel extract -F babel.cfg -o messages.pot --input-dirs=. --no-wrap
```




