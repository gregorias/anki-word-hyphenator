# -*- coding: utf-8 -*-
"""The implementation of the word hyphenator plugin."""
import os.path
import re
import sys
from typing import List, Optional

sys.path.append(os.path.dirname(__file__))

import aqt  # type: ignore
import bs4  # type: ignore
from aqt import gui_hooks  # type: ignore
from aqt.utils import showWarning  # type: ignore
from bs4 import BeautifulSoup, NavigableString  # type: ignore

# Import locally in case we are executing as a packaged Anki addon
try:
    from . import langdetect  # type: ignore
except ImportError:
    import langdetect  # type: ignore

try:
    from . import pyphen  # type: ignore
except ImportError:
    import pyphen  # type: ignore

addon_path = os.path.dirname(__file__)
config = aqt.mw and aqt.mw.addonManager.getConfig(__name__)


def get_config(key: str, default):
    return (config and config.get(key, default)) or default


SHY = '\xad'


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
            new_chunks.append(dic.inserted(chunk, SHY))
    return ''.join(new_chunks)


def hyphenate_end_node(dic, text: str) -> str:
    output = hyphenate_single_words(dic, text)

    find_hyphen_in_mathjax = r'\\\((.*?)' + SHY + r'(.*?)\\\)'
    while re.search(find_hyphen_in_mathjax, output):
        output = re.sub(find_hyphen_in_mathjax, r'\(\1\2\)', output)

    find_hyphen_in_mathjax = r'\\\[(.*?)' + SHY + r'(.*?)\\\]'
    while re.search(find_hyphen_in_mathjax, output):
        output = re.sub(find_hyphen_in_mathjax, r'\[\1\2\]', output)

    return output


def should_ignore(text):
    return bool(re.match(r'\[[^\]]+\]', text))


def only_printable(text: str) -> str:
    return str.join('', filter(lambda x: x.isprintable(), text))


def is_stylesheet_implemented() -> bool:
    return getattr(bs4.element, 'Stylesheet', None) is not None


class DfsStack:

    def __init__(self, initial_nodes):
        self.nodes = list(initial_nodes)

    def __iter__(self):
        return self

    def __next__(self):
        if self.nodes:
            top = self.nodes[-1]
            self.nodes.pop()
            return top
        else:
            raise StopIteration()

    def send(self, new_nodes: List[bs4.PageElement]):
        self.nodes.extend(list(new_nodes))


def visit_and_hyphenate(
        node: bs4.PageElement) -> Optional[List[bs4.PageElement]]:
    """Visits HTML nodes and hyphenates text.

    Returns:
        Children of tag elements that should be further processed, e.g., <pre>
        elements are skipped.
    """
    if isinstance(node, bs4.Comment):
        return None

    # We check whether `Stylesheet` is implemented, because it's a
    # relatively recent addition to BeautifulSoup
    # (https://bazaar.launchpad.net/~leonardr/beautifulsoup/bs4/revision/564).
    # In case it is not, we don't skip <style> nodes. This will mangle
    # stylesheets if they exist, but that is a cost I'm willing to take.
    if (is_stylesheet_implemented()
            and isinstance(node, bs4.element.Stylesheet)):
        return None

    if isinstance(node, bs4.Tag):
        if node.name == 'pre':
            return None
        if node.name == 'style':
            return None
        return node.children

    if not isinstance(node, bs4.NavigableString):
        return None

    # My intention is to remove silent-hyphens, so that language detection
    # works correctly.
    printable_text = only_printable(node)
    if should_ignore(printable_text):
        return None

    try:
        lang = langdetect.detect(printable_text)
        if lang == 'en':
            # Use US dictionary for English, because it seems that the US
            # dictionary is richer. For example en_GB doesn't hyphenate
            # "format," but US does ("for-mat").
            lang = 'en_US'
        dic = pyphen.Pyphen(lang=lang)
    except (langdetect.lang_detect_exception.LangDetectException, KeyError):
        return None

    new_text = hyphenate_end_node(dic, node)
    node.replaceWith(new_text)
    return None


def walk(soup: bs4.BeautifulSoup, func):
    dfs_stack = DfsStack(soup.children)
    for node in dfs_stack:
        maybe_more_nodes = func(node)
        if maybe_more_nodes:
            dfs_stack.send(maybe_more_nodes)


def hyphenate(html: str) -> str:
    """Hyphenates the HTML document.

    >>> hyphenate('<div>&asymp; hyphenation</div>')
    '<div>&asymp; hy&shy;phen&shy;ation</div>')

    Returns:
        An HTML5-encoded string with hyphenation.
    """
    soup = BeautifulSoup(html, features='html.parser')
    walk(soup, visit_and_hyphenate)
    return str(soup.encode(formatter='html5'), 'utf8')


def use_minimal_html_formatting(html: str) -> str:
    """Reformats the HTML string using minimal encoding."""
    bs = BeautifulSoup(html, features='html.parser')
    return str(bs.encode(formatter='minimal'), 'utf8')


def hyphenate_action(editor) -> None:
    if editor.currentField is None:
        showWarning(
            "You've run the word hyphenator without selecting a field.\n" +
            "Please select a note field before running the word hyphenator.")
        return None

    field = editor.note.fields[editor.currentField]
    new_field_with_html5 = hyphenate(field)
    # Reformatting is necessary, because
    # * hyphenate('<img src="berührung">') == '<img src="ber&uuml;hrung"/>'
    # * Anki desktop wouldn't display the `berührung` image when
    #   `src="ber&uuml;hrung"` (even though it's valid HTML
    #   (https://bit.ly/3ewd4bj)
    new_field = use_minimal_html_formatting(new_field_with_html5)
    editor.note.fields[editor.currentField] = new_field

    # That's how aqt.editor.onHtmlEdit saves cards.
    # It's better than `editor.mw.reset()`, because the latter loses focus.
    # Calls like editor.mw.reset() or editor.loadNote() are necessary to save
    # HTML changes.
    if not editor.addMode:
        editor.note.flush()
    editor.loadNoteKeepingFocus()


def on_editor_buttons_init(buttons: List, editor) -> None:
    #  Don’t use `ctrl-h`. `cmd-h` is already taken by MacOS to hide windows.
    shortcut = get_config("shortcut", "ctrl+-")
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
