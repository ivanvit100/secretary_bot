from i18n import ru, en
import config

languages = {
    "ru": ru.messages,
    "en": en.messages
}

def get_message(key, **kwargs):
    lang = config.get_language()
    message = languages.get(lang, languages["ru"]).get(key, f"Missing key: {key}")
    
    if kwargs:
        try:
            return message.format(**kwargs)
        except KeyError:
            return message
    return message

def _(key, **kwargs):
    return get_message(key, **kwargs)