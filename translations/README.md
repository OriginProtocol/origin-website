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

## New translation files

After downloading or manual edits to `.po` files, you must compile translations:
```
pybabel compile -f -d  translations
```
(The `-f` flag is needed to force the compile, since downloads from Google translator are always marked as 'fuzzy')


## Fresh Start

Use this command to start from scratch, extracting strings into a file `messages.pot`
```
pybabel extract -F babel.cfg -o messages.pot --input-dirs=. --no-wrap
```



