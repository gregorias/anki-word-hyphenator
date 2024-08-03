# Anki Word Hyphenator

An Anki plugin that hyphenates words during editing.

<p align="center">
  <img src="images/demo.gif" alt="a GIF showing Hyphenator at work"/>
</p>

## Installation

### From AnkiWeb

You can install directly from
[AnkiWeb](https://ankiweb.net/shared/info/1140138750) using Anki’s addon
management.

### From GitHub Releases

You can fetch an addon package from [the GitHub Releases
tab](https://github.com/gregorias/anki-word-hyphenator/releases).

### From Source

1. Run `package` from the main directory. This will create
   `wordhyphenator.ankiaddon`.
2. Import `wordhyphenator.ankiaddon` in Anki.

## 🚀 Usage

1. Write some text in a field.
2. Press `CTRL+-` (on macOS, `⌘+-`) or click this add-on’s button in the
   editor’s button bar.

## ⚙️ Configuration

The addon accepts the following configuration options:

* `shortcut` (default: `"ctrl+-"` or `"cmd+-"`) — The keyboard shortcut for the
  hyphenation action.
* `apply_on_note_flush` (default: `false`) — Whether to apply the hyphenation
  action on note saves. This feature is experimental. Let the maintainer
  know if there any issues.
