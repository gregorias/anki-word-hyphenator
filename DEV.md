# 🛠️ Developer documentation

This is a documentation file for this plugin's developers.

## Dev environment setup

This project requires

- [Lefthook](https://github.com/evilmartians/lefthook)
- [Commitlint](https://github.com/conventional-changelog/commitlint)

1. Run `git submodule sync` to initialize the repository after cloning.

1. Install the required Python version:

    ```shell
    pyenv install
    ```

1. Set up Pipenv:

    ```shell
    pipenv install --dev
    ```

1. Install Lefthook:

    ```shell
    lefthook install
    ```

## Testing

1. Run unit tests and MyPy with `testall`.
2. Test supported Anki versions (2.1.49 and latest) by packaging the
   plugin and importing the plugin into the lowest and the newest
   support Anki.

## Runtime dependencies

Pyphen stopped working with Python 3.9 after 0.13.2, so keep it pinned
at 0.13.2. We can't update Python, because as of 2023-11-03, Anki uses
Python 3.9.

I include six.py, because [langdetect needs
it](https://github.com/Mimino666/langdetect/blob/a1598f1afcbfe9a758cfd06bd688fbc5780177b2/langdetect/detector.py#L4).

## Release & distribution

1. Create a release commit.
    1. Bump up the package version in `wordhyphenator/manifest.json`.
    2. Tag the release commit `git tag vx.y.z && git push origin vx.y.z`.
1. Use the `dev/bin/package` tool to create `wordhyphenator.ankiaddon`.
1. Create a GitHub release: `gh release create vx.y.z wordhyphenator.ankiaddon`.
1. [Share the package on Anki.](https://addon-docs.ankiweb.net/#/sharing)
