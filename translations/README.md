# Localization

## Status 2018-01-31

| Code | Language | Translator(s) | Status |
| ---- | -------- | ------------- | ------ |
| ar | Arabic | m.alqattan | 🚧 In Progress |
| cs | Czech | Daosta | 🚧 In Progress |
| de | German | Filip | ✅ Complete |
| el | Greek | Tasso | ✅ Complete |
| es | Spanish | funk | ✅ Complete |
| fr | French | Bastien |  ✅ Complete |
| he | Hebrew | | | |
| hr | Croatian | Filip | ✅ Complete |
| it | Italian | funk |  ✅ Complete |
| ja | Japanese | | | |
| ko | Korean | stellayujinlee |  🚧 In Progress |
| nl | Dutch | Yasinz | ✅ Complete |
| pt | Portugese | | | |
| ru | Russian | Alex K | ✅ Complete |
| th | Thai | Ben V / @cvibhagool | ✅ Complete |
| zh_Hans | Chinese (Simplified) | Anson | ✅ Complete |
| zh_Hant | Chinese (Traditional) | Anson | ✅ Complete |

## Implementation

Localization is done with the [Flask-Babel](https://pythonhosted.org/Flask-Babel/) module.

Translated files live in `translations/<Language Code>/LC_MESSAGES/messages.po`.

- `../messages.pot` file contains found English strings. This is the "master list" of strings needing translation.
- `messages.po` files contain specific language translations.
- `messages.mo` files are binary, compiled versions of the `.po` files and should never be edited directly.

## Extract new/edited English strings for translation

1. Search source files and extract strings into a file `messages.pot`

```
pybabel extract -F babel.cfg -o messages.pot --input-dirs=. --no-wrap
```

2. Update `.po` translations with new strings.

```
pybabel update -i messages.pot -d translations --no-wrap
```

The `.po` files are now ready for translation.

## Updating translations on website

1. Download the new translation from Google Translator Toolkit. The file will be called `archive.zip` by default.

2. In the `translations` directory, run:

```
python extract_po_files_from_gtt_zip.py ~/Downloads/archive.zip
```
This will grab the new `.po` files for each langauge, and copy them to the correct place. Note this will overwrite the existing `.po` files.

3. Fix common errors:

```
python fix_po_files.py
```

4. Compile translations into `.mo` files:

```
pybabel compile -f -d  .
```
The `-f` flag is needed to force the compile, since downloads from Google translator are always marked as 'fuzzy'

Note: `.mo` files must committed in the repo in order for them to get on heroku.

5. From repo root directory, run the website code to see new translations:

```
python main.py
```

## Adding a new language

```
pybabel init -i messages.pot -d translations -l <Language Code>
```
See [pybabel docs for init](http://babel.pocoo.org/en/latest/cmdline.html#init)

This will create the directory structure and initial `.po` file.

Edit `config/constants.py` and add the language-code under `LANGUAGES`

### Test

In the `company-website` directory, run:
```
python main.py
```
And you should see the new language on the site.

## Troubleshooting

If you get this error:
```
  File "/Users/stan/Documents/Origin/company-website/lib/python2.7/site-packages/babel/messages/pofile.py", line 147, in _add_message
    string = self.translations[0][1].denormalize()
IndexError: list index out of range
```
It most likely means that you have a `%` in a `msgstr`. These must be escaped as `%%`.
