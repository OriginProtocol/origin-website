# Localization

Localization is done with the [Flask-Babel](https://pythonhosted.org/Flask-Babel/) module.

Translated files live in `translations/<Language Code>/LC_MESSAGES/messages.po`.

- `.pot` file contains found English strings. This is the "master list" of strings to translate.
- `.po` files contain speicific language translations.

## New English strings

1. Search source files and extract strings into a file `messages.pot`
```
pybabel extract -F babel.cfg -o messages.pot --input-dirs=. --no-wrap
```

2. Update `.po` translations with new strings.
```
pybabel update -i messages.pot -d translations --no-wrap
```

## New or updated translation files

After downloading or manual edits to `.po` files, you must compile translations:
```
pybabel compile -f -d  translations
```
(The `-f` flag is needed to force the compile, since downloads from Google translator are always marked as 'fuzzy')

If you get an error `ValueError: expected only letters, got u''`, run the python script `fix_po_files.py`. This error is caused by a `.po` file containg an empty language header: `"Language: \n"`, where it should be e.g. `"Language: de\n"`

This step will generate compiled `.mo` files from each `.po`.  These are the files used to actaully render translated versions of the site.

Note: `.po` files must committed in the repo in order for them to get on heroku.

## Add New language

```
pybabel init -i messages.pot -d translations -l <Language Code>
```
See [pybabel docs for init](http://babel.pocoo.org/en/latest/cmdline.html#init)





