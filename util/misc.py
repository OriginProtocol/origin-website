from pyuca import Collator

from flask import request
from flask_babel import Locale

from config import constants

import re
import os

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

def resolve_inline_css_imports(filename, file_contents):
    """
    Replaces the `import()` statement with those files contents
    Open Ended Question: What happens with cyclic import?
    """
    # Array of relative CSS URLs
    matches = re.findall(r'\@import url\([\'\"]([^\)]+)[\'\"]\);', file_contents)

    # Base path of the file
    basePath = os.path.split(filename)[0]
    
    normalizedFilenames = [os.path.normpath(os.path.join(basePath, relativeUrl)) for relativeUrl in matches]

    contents = ["/* %s */\n\n %s" % (filename, file_get_contents(filename)) for filename in normalizedFilenames]
    contents.append(file_contents.replace('@import url(', '// Resolved: @import url('))
    return "\n\n\n\n".join(contents)

def file_get_contents(filename):
    """
    Returns file contents as a string.
    """
    with open(filename) as file:
        if filename.endswith(".css"):
            return resolve_inline_css_imports(filename, file.read())
        else:
            return file.read()

def concat_asset_files(filenames):
    """
    Concats css or javascript files together with a comment containing the filename
    at the top of each file.
    """
    contents = ["/* %s */\n\n %s" % (filename, file_get_contents(filename)) for filename in filenames]
    return "\n\n\n\n".join(contents) 