# Anki Word Hyphenator

An Anki plugin that hyphenates words during editing.

## Installation From Source

1. Run `package` from the main directory. This will create
   `wordhyphenator.ankiaddon`.
2. Import `wordhyphenator.ankiaddon` in Anki.

## For Developers

Run `git submodule sync` to initialize the repository after cloning.

Use direnv to set up the development environment (see `.envrc`).

### Testing

Run `testall` to run Mypy and unit tests.

### Distribution

See [Anki's documentation on sharing
add-ons](https://addon-docs.ankiweb.net/#/sharing).
