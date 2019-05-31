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

1. Look at the GitHub PR called _New Crowdin translations_ which is generated and maintained automatically by Crowdin. This PR will always contain the latest `.po` files from our translators. Locally, merge this PR into `master` for testing.

2. If you're using Docker, you'll probably want to ssh into it, and then cd into the translations dir. (This will have the virtual environment set up with the pybabel tools.)

```
docker exec -it origin-website /bin/bash
# Then, in the container
cd translations
```

3. Fix common errors:

```
python fix_po_files.py
```

4. Compile translations into `.mo` files:

```
pybabel compile -f -d  .
```
The `-f` flag may be needed for entries that are marked as 'fuzzy'

5. Run the website locally to ensure things look good. (`python main.py` or restart docker container.)

6. Add and commit the  compiled `.mo` files. This is requried to get them onto heroku.

```
git add *.mo
git add *.po
git commit -m "New translations compiled."
```

7. Merge to master, and push to heroku.

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
