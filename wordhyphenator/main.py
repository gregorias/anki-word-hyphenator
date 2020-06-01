# -*- coding: utf-8 -*-
"""The implementation of the word hyphenator plugin."""
import os.path
import re
from typing import List, Optional

import aqt
from aqt import gui_hooks
from aqt.utils import showWarning
import bs4  # type: ignore
from bs4 import BeautifulSoup, NavigableString  # type: ignore

# Import locally in case we are executing as a packaged Anki addon
try:
    from . import langdetect # type: ignore
except ImportError:
    import langdetect # type: ignore

try:
    from . import pyphen # type: ignore
except ImportError:
    import pyphen # type: ignore


addon_path = os.path.dirname(__file__)
config = aqt.mw and aqt.mw.addonManager.getConfig(__name__)


def get_config(key: str, default):
    return (config and config.get(key, default)) or default


SHY_ENT = '&shy;'


def chunkify(text: str) -> List[str]:
    # Do not match HTML entities
    html_entities = re.compile('(&[a-zA-Z]+;)')
    words = re.compile(r'(\b\w+\b)')
    chunks = []
    non_word_chunks = []
    for i, chunk in enumerate(html_entities.split(text)):
        if i % 2 == 0:
            for j, word in enumerate(words.split(chunk)):
                if j % 2 == 0:
                    non_word_chunks.append(word)
                else:
                    chunks.append(''.join(non_word_chunks))
                    non_word_chunks = []
                    chunks.append(word)
        else:
            non_word_chunks.append(chunk)
    chunks.append(''.join(non_word_chunks))
    return chunks


def hyphenate_single_words(dic, text: str) -> str:
    new_chunks = []
    for i, chunk in enumerate(chunkify(text)):
        if i % 2 == 0:
            new_chunks.append(chunk)
        else:
            new_chunks.append(dic.inserted(chunk, str(SHY_ENT)))
    return ''.join(new_chunks)


def hyphenate_end_node(dic, text: str) -> str:
    output = hyphenate_single_words(dic, text)

    find_hyphen_in_mathjax = r'\\\((.*?)&shy;(.*?)\\\)'
    while re.search(find_hyphen_in_mathjax, output):
        output = re.sub(find_hyphen_in_mathjax, r'\(\1\2\)', output)

    find_hyphen_in_mathjax = r'\\\[(.*?)&shy;(.*?)\\\]'
    while re.search(find_hyphen_in_mathjax, output):
        output = re.sub(find_hyphen_in_mathjax, r'\[\1\2\]', output)

    return output


def should_ignore(text):
    return bool(re.match(r'\[[^\]]+\]', text))


def only_printable(text: str) -> str:
    return str.join('', filter(lambda x: x.isprintable(), text))


def encode_navigable_string(ns: NavigableString) -> str:
    return BeautifulSoup(
        ns, features='html.parser').encode(formatter='html5').decode('UTF-8')


def hyphenate(html: str) -> str:
    bs = BeautifulSoup(html, features='html.parser')
    text_nodes = bs.findAll(text=True)
    for text_node in text_nodes:
        printable_text = only_printable(text_node)
        if should_ignore(printable_text):
            continue
        try:
            lang = langdetect.detect(printable_text)
            if lang == 'en':
                # Use US dictionary for English, because it seems that the US
                # dictionary is richer. For example en_GB doesn't hyphenate
                # "format," but US does ("for-mat").
                lang = 'en_US'
            dic = pyphen.Pyphen(lang=lang)
        except (langdetect.lang_detect_exception.LangDetectException, KeyError):
            continue

        # hyphenate_end_node expect HTML-encoded text, e.g., '&shy;'s not
        # '\xad's, so encode text_node.
        new_text = hyphenate_end_node(dic, encode_navigable_string(text_node))
        # Decode HTML back for replacing with BeautifulSoup
        text_node.replaceWith(BeautifulSoup(new_text, features='html.parser'))
    return bs.prettify(formatter='html5')


def hyphenate_action(editor) -> None:
    if editor.currentField is None:
        showWarning(
            "You've run the word hyphenator without selecting a field.\n" +
            "Please select a note field before running the word hyphenator.")
        return None

    field = editor.note.fields[editor.currentField]
    new_field = hyphenate(field)
    editor.note.fields[editor.currentField] = new_field
    # That's how aqt.editor.onHtmlEdit saves cards.
    # It's better than `editor.mw.reset()`, because the latter loses focus.
    # Calls like editor.mw.reset() or editor.loadNote() are necessary to save
    # HTML changes.
    if not editor.addMode:
        editor.note.flush()
    editor.loadNoteKeepingFocus()


def on_editor_buttons_init(buttons: List, editor) -> None:
    shortcut = get_config("shortcut", "ctrl+h")
    icon_path = os.path.join(addon_path, "icons", "silent hyphen.png")
    css = editor.addButton(
        icon=icon_path,
        cmd="hyphenate",
        func=hyphenate_action,
        tip="Hyphenate words ({})".format(shortcut),
        # Skip label, because we already provide an icon.
        keys=shortcut)
    buttons.append(css)


gui_hooks.editor_did_init_buttons.append(on_editor_buttons_init)
