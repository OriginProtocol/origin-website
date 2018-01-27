# Localization

## Status 2018-01-26

| Code | Language | Translator(s) | Status |
| ---- | -------- | ------------- | ------ |
| ar | Arabic | m.alqattan | 🚧 In Progress |
| cs | Czech | Daosta | 🚧 In Progress |
| de | German | Filip | ✅ Complete |
| el | Greek | Tasso | ✅ Complete |
| es | Spanish | funk | ✅ Complete |
| fr | French | JB, Aline | 🚧 In Progress |
| he | Hebrew | | | |
| hr | Croatian | Filip | ✅ Complete |
| it | Italian | funk | 🚧 In Progress |
| ja | Japanese | | | |
| ko | Korean | | | |
| nl | Dutch | Yasinz | ✅ Complete |
| pt | Portugese | | | |
| ru | Russian | Alex K | ✅ Complete |
| th | Thai | Ben V | 🚧 In Progress |
| zh_Hans | Chinese (Simplified) | Anson | 🚧 In Progress |
| zh_Hant | Chinese (Traditional) | Anson | 🚧 In Progress |

## Implementation

Localization is done with the [Flask-Babel](https://pythonhosted.org/Flask-Babel/) module.

Translated files live in `translations/<Language Code>/LC_MESSAGES/messages.po`.

- `../messages.pot` file contains found English strings. This is the "master list" of strings needing translation.
- `messages.po` files contain specific language translations.
- `messages.mo` files are binary, compiled versions of the `.po` files and should never be edited directly.

## Updating for new/edited English strings

1. Search source files and extract strings into a file `messages.pot`
```
pybabel extract -F babel.cfg -o messages.pot --input-dirs=. --no-wrap
```

2. Update `.po` translations with new strings.
```
pybabel update -i messages.pot -d translations --no-wrap
```

The `.po` files are now ready for translation.

## Adding/updating translations

After downloading or manual edits to `.po` files, you must compile translations:
```
pybabel compile -f -d  translations
```
(The `-f` flag is needed to force the compile, since downloads from Google translator are always marked as 'fuzzy')

If you get an error `ValueError: expected only letters, got u''`, run the python script `fix_po_files.py`. This error is caused by a `.po` file containg an empty language header: `"Language: \n"`, where it should be e.g. `"Language: de\n"`

This step will generate compiled `.mo` files from each `.po`.  These binary files used to actaully render translated versions of the site.

Note: `.mo` files must committed in the repo in order for them to get on heroku.

## Add New language

```
pybabel init -i messages.pot -d translations -l <Language Code>
```
See [pybabel docs for init](http://babel.pocoo.org/en/latest/cmdline.html#init)

Be sure to add any new language to `config/constants.py` for it to be appear.



