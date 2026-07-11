# 🛠️ Developer documentation

This is a documentation file for this plugin's developers.

## Dev environment setup

This project requires the following tools:

- [Commitlint](https://github.com/conventional-changelog/commitlint)
- [Lefthook](https://github.com/evilmartians/lefthook)
- [Just]
- [Pyenv]
- [Uv]

1. Run `git submodule sync` to initialize the repository after cloning.

1. Install the required Python version:

   ```shell
   pyenv install
   ```

1. Set up a local virtual environment:

   ```shell
   uv venv
   ```

1. Install development dependencies:

   ```shell
   uv pip install --group dev
   ```

1. Install Lefthook:

   ```shell
   lefthook install
   ```

## Testing

1. Run unit tests and MyPy with `testall`.
2. Test supported Anki versions (2.1.49 and latest) by packaging the plugin and
   importing the plugin into the lowest and the newest support Anki.

## Updating Python

This package sets up a specific Python version to keep the dev environment in
sync with what Anki uses.
To update this Python version, you need to:

1. Run `uv python pin 3.X.Y`.
   This will update `.python-version` and the `requires-python` field in
   `pyproject.toml`.
2. Run `uv sync --locked`.
   This will update the local venv to the pinned version.
3. Delete the Mypy cache:
   `rm -r .mypy_cache`.

## Runtime dependencies

### Updating

To update dependencies, go to their directory and run `git pull`, possibly you
need to checkout main.
Go back to the parent repository and commit changes.

### Notes

Before July 2024, Pyphen stopped working with Python 3.9 after 0.13.2, so I kept
it pinned at 0.13.2.
We couldn’t update Python, because as of 2023-11-03, Anki uses Python 3.9.

I include six.py, because
[langdetect needs it](https://github.com/Mimino666/langdetect/blob/a1598f1afcbfe9a758cfd06bd688fbc5780177b2/langdetect/detector.py#L4).

## Release & distribution

1. Create a release commit.
   1. Bump up the package version in `wordhyphenator/manifest.json`.
   2. Tag the release commit `git tag vx.y.z && git push origin vx.y.z`.
1. Use the `dev/bin/package` tool to create `wordhyphenator.ankiaddon`.
1. Create a GitHub release:
   `gh release create vx.y.z wordhyphenator.ankiaddon`.
1. [Share the package on Anki.](https://addon-docs.ankiweb.net/#/sharing)
