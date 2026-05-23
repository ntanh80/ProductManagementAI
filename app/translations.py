"""Simple JSON-based translation service for ProductManagementAI."""
import json
import os
from flask import session, request

_translations = {}

TRANSLATION_DIR = os.path.join(os.path.dirname(__file__), 'translations')

SUPPORTED_LANGUAGES = {
    'vi': 'Tiếng Việt',
    'en': 'English',
}

DEFAULT_LANGUAGE = 'vi'


def load_translations(lang):
    """Load translation dictionary for a given language."""
    path = os.path.join(TRANSLATION_DIR, f'{lang}.json')
    if not os.path.exists(path):
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_language():
    """Get current language: URL param > session > default."""
    lang = request.args.get('lang', '')
    if lang in SUPPORTED_LANGUAGES:
        session['lang'] = lang
        return lang
    lang = session.get('lang', DEFAULT_LANGUAGE)
    if lang not in SUPPORTED_LANGUAGES:
        lang = DEFAULT_LANGUAGE
    return lang


def get_translations(lang):
    """Get translations for language, cached in module."""
    if lang not in _translations:
        _translations[lang] = load_translations(lang)
    return _translations[lang]


def translate(text, lang=None):
    """Translate a string from Vietnamese to the target language."""
    if lang is None:
        lang = get_language()
    if lang == DEFAULT_LANGUAGE:
        return text
    translations = get_translations(lang)
    return translations.get(text, text)
