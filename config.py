LANGUAGE = "ru"
AVAILABLE_LANGUAGES = ["ru", "en"]
NAME = "Иванущенко Виталия"
UTC = 3
MODULES = {
    "balance": True,
    "email": True,
    "files": True,
    "notification": True,
    "plots": True,
    "support": True,
    "task": True,
    "vps": True
}

def set_language(lang_code):
    global LANGUAGE
    if lang_code in AVAILABLE_LANGUAGES:
        LANGUAGE = lang_code
        return True
    return False

def get_language():
    return LANGUAGE