import json
import os

# File path to store user language preferences
USER_PREF_FILE = 'user_languages.json'

# Language mapping dictionary
language_mapping = {
    '1': 'EN',
    '2': 'FR'
}

# Load translations from the JSON file with UTF-8 encoding
def load_translations():
    with open('translations.json', 'r', encoding='utf-8') as file:
        return json.load(file)

translations = load_translations()

def load_token():
    with open('config.json', 'r', encoding='utf-8') as file:
        config = json.load(file)
        return config['TOKEN']

def load_user_languages():
    if os.path.exists(USER_PREF_FILE):
        with open(USER_PREF_FILE, 'r', encoding='utf-8') as file:
            data = json.load(file)
            # Convert keys from strings back to integers
            return {int(user_id): language for user_id, language in data.items()}
    return {}

# Save user language preferences to the JSON file
def save_user_languages(user_languages):
    with open(USER_PREF_FILE, 'w', encoding='utf-8') as file:
        json.dump(user_languages, file, ensure_ascii=False, indent=4)