# Localization

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

When the `.po` files are pushed to any branch in the GitHub repo, they will be synced automatically with Crowdin for translation.

## Updating translations on website

1. Look at the GitHub PR called "New Crowdin translations" which is generated and maintained automatically by Crowdin. This PR will always contain the latest `.po` files from our translators. Manually copy and paste whatever `.po` files you want from that PR and place the files in the `LC_MESSAGES` directory for the appropriate language.

2. Fix common errors:

```
python fix_po_files.py
```

3. Compile translations into `.mo` files:

```
pybabel compile -f -d  .
```
The `-f` flag is needed to force the compile, since downloads from Google translator are always marked as 'fuzzy'

Note: `.mo` files must committed in the repo in order for them to get on heroku.

4. From repo root directory, run the website code to see new translations:

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

In the `origin-website` directory, run:
```
python main.py
```
And you should see the new language on the site.

## Troubleshooting

If you get this error:
```
  File "/Users/stan/Documents/Origin/origin-website/lib/python2.7/site-packages/babel/messages/pofile.py", line 147, in _add_message
    string = self.translations[0][1].denormalize()
IndexError: list index out of range
```
It most likely means that you have a `%` in a `msgstr`. These must be escaped as `%%`.
