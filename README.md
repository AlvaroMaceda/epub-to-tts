# TTS Audiobook Generator

Convert EPUB books into audiobooks using Google Text-to-Speech (gTTS).

## Installation

1. Make sure you have Python 3.12 or newer installed.
2. Install Poetry (if not already):
   ```sh
   pip install poetry
   ```
3. Install dependencies:
   ```sh
   poetry install
   ```

## How to Run

Run the script from the command line:

```sh
poetry run python main.py <audiobook.epub> [--language <lang>] [--tld <tld>]
```

- `<audiobook.epub>`: Path to your EPUB file (required)
- `--language` or `--lang`: Language code (optional, default: `en`)
- `--tld`: Top-level domain for accent (optional, default: `com`)

### Example

```sh
poetry run python main.py mybook.epub --language es --tld com.mx
```

All audio files will be saved in the `audio_chapters` folder.

---

See `pyproject.toml` for project metadata and packaging info.
