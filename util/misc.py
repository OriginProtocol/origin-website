from pyuca import Collator

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
