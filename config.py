LANGUAGE = "ru"
AVAILABLE_LANGUAGES = ["ru", "en"]
NAME = "Иванущенко Виталия"

def set_language(lang_code):
    global LANGUAGE
    if lang_code in AVAILABLE_LANGUAGES:
        LANGUAGE = lang_code
        return True
    return False

def get_language():
    return LANGUAGE