import os
from ebooklib import epub
from bs4 import BeautifulSoup
from gtts import gTTS
import re
import argparse

# -----------------------
# Configuration
# -----------------------
OUTPUT_FOLDER = 'audio_chapters'
MAX_CHARS = 4000                # Max chars per TTS request

# -----------------------
# Helpers
# -----------------------
def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "_", name)

def chunk_text(text, max_len=MAX_CHARS):
    chunks = []
    start = 0
    while start < len(text):
        end = start + max_len
        if end < len(text):
            # Try to break at last sentence
            last_dot = text.rfind('.', start, end)
            if last_dot != -1:
                end = last_dot + 1
        chunks.append(text[start:end].strip())
        start = end
    return chunks

def main():
    parser = argparse.ArgumentParser(description="EPUB to Audiobook Converter")
    parser.add_argument("audiobook", type=str, help="Path to the EPUB file")
    parser.add_argument("--language", "--lang", type=str, default="en", help="Language code (default: en)")
    parser.add_argument("--tld", type=str, default="com", help="Top-level domain for accent (default: com)")
    args = parser.parse_args()

    EPUB_FILE = args.audiobook
    LANG = args.language
    TLD = args.tld

    book = epub.read_epub(EPUB_FILE)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    chapter_number = 1
    for item in book.get_items_of_type(epub.ITEM_DOCUMENT):
        soup = BeautifulSoup(item.get_content(), 'html.parser')
        chapter_text = soup.get_text().strip()
        if chapter_text:
            title = soup.title.string if soup.title else f'Chapter_{chapter_number}'
            title = sanitize_filename(title[:50])
            print(f"Processing {title}...")
            chunks = chunk_text(chapter_text, MAX_CHARS)
            for i, chunk in enumerate(chunks, start=1):
                filename = f"{OUTPUT_FOLDER}/{title}_part{i}.mp3" if len(chunks) > 1 else f"{OUTPUT_FOLDER}/{title}.mp3"
                tts = gTTS(text=chunk, lang=LANG, tld=TLD)
                tts.save(filename)
            chapter_number += 1
    print(f"Done! All chapters saved in '{OUTPUT_FOLDER}'")

if __name__ == "__main__":
    main()
