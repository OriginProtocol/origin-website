from pyuca import Collator


from flask import request
from flask_babel import Locale

from config import constants


def sort_language_constants():
    """
    function to generate correct ordering of constants.LANGUAGES list
    sorted by Unicode characters
    """
    c = Collator()
    lang_names = [Locale(lang).get_language_name(lang).capitalize()
                  for lang in constants.LANGUAGES]
    available_languages = dict(zip(lang_names, constants.LANGUAGES))
    sorted_lang_names = sorted(lang_names, key=c.sort_key)

    return [available_languages[lang_name] for lang_name in sorted_lang_names]


def get_real_ip():
    """
    Returns the client IP from the headers, fallbacks to remote_addr
    """
    if 'X-Forwarded-For' in request.headers:
        return request.headers.getlist("X-Forwarded-For")[0].rpartition(' ')[-1]
    else:
        return request.remote_addr or 'untrackable'

def file_get_contents(filename):
    """
    Returns file contents as a string.
    """
    with open(filename) as file:
        return file.read()

def concat_asset_files(filenames):
    """
    Concats css or javascript files together with a comment containing the filename
    at the top of each file.
    """
    contents = ["/* %s */\n\n %s" % (filename, file_get_contents(filename)) for filename in filenames]
    return "\n\n;\n\n".join(contents) 