import os
from ebooklib import epub, ITEM_DOCUMENT
from bs4 import BeautifulSoup
import re
import argparse
import asyncio
from edge_tts import Communicate

# -----------------------
# Configuration
# -----------------------
OUTPUT_FOLDER = "audio_chapters"
MAX_CHARS = 4000  # Max chars per TTS request


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
            last_dot = text.rfind(".", start, end)
            if last_dot != -1:
                end = last_dot + 1
        chunks.append(text[start:end].strip())
        start = end
    return chunks


def main():
    parser = argparse.ArgumentParser(description="EPUB to Audiobook Converter")
    parser.add_argument("audiobook", type=str, help="Path to the EPUB file")
    parser.add_argument(
        "--voice",
        type=str,
        default="en-US-JennyNeural",
        help="Voice for TTS (default: en-US-JennyNeural)",
    )
    parser.add_argument(
        "--rate", type=str, default=None, help="Speech rate (e.g. '+20%')"
    )
    parser.add_argument(
        "--pitch", type=str, default=None, help="Speech pitch (e.g. '+5Hz')"
    )
    parser.add_argument(
        "--volume", type=str, default=None, help="Speech volume (e.g. '+10dB')"
    )
    parser.add_argument(
        "--start-chapter",
        type=int,
        default=1,
        help="Start from this chapter number (1-indexed, default: 1)",
    )
    parser.add_argument(
        "--end-chapter",
        type=int,
        default=None,
        help="End at this chapter number (1-indexed, optional)",
    )
    args = parser.parse_args()

    EPUB_FILE = args.audiobook
    VOICE = args.voice
    RATE = args.rate
    PITCH = args.pitch
    VOLUME = args.volume
    START_CHAPTER = args.start_chapter
    END_CHAPTER = args.end_chapter

    print(f"Using voice: {VOICE}")
    if RATE:
        print(f"Rate: {RATE}")
    if PITCH:
        print(f"Pitch: {PITCH}")
    if VOLUME:
        print(f"Volume: {VOLUME}")
    book = epub.read_epub(EPUB_FILE)

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    chapter_num = 0

    for idx, item in enumerate(book.get_items_of_type(ITEM_DOCUMENT)):

        soup = BeautifulSoup(item.get_content(), "html.parser")
        chapter_text = soup.get_text().strip()
        if not chapter_text:
            continue

        chapter_num +=1

        # print(f"Chapter index: {idx} chapter num: {chapter_num} start_chapter: {START_CHAPTER} end_chapter: {END_CHAPTER}")
        if chapter_num < START_CHAPTER:
            # print(f"skipping chapter {chapter_num}, start chapter is {START_CHAPTER}")
            continue
        if END_CHAPTER is not None and chapter_num > END_CHAPTER:
            # print(f"end chapter reached: {END_CHAPTER}")
            # print(f"chapter num: {chapter_num}")
            break

        print(f"Chapter {chapter_num} length: {len(chapter_text)} characters")
        title = soup.title.string if soup.title else f"Chapter_{chapter_num}"
        title = sanitize_filename(title[:50])
        print(f"Processing {title}...")
        chunks = chunk_text(chapter_text, MAX_CHARS)

        async def save_chunk(chunk, filename, voice=VOICE, chunk_num=1):
            if chunk_num > 1:
                print(f"  Processing chunk {chunk_num} for {filename}...")
            kwargs = {}
            if RATE is not None:
                kwargs["rate"] = RATE
            if PITCH is not None:
                kwargs["pitch"] = PITCH
            if VOLUME is not None:
                kwargs["volume"] = VOLUME
            communicate = Communicate(chunk, voice, **kwargs)
            await communicate.save(filename)

        async def process_chunks():
            tasks = []
            for i, chunk in enumerate(chunks, start=1):
                filename = (
                    f"{OUTPUT_FOLDER}/{title}_part{i}.mp3"
                    if len(chunks) > 1
                    else f"{OUTPUT_FOLDER}/{title}.mp3"
                )
                tasks.append(save_chunk(chunk, filename, VOICE, chunk_num=i))
                await asyncio.gather(*tasks)

        asyncio.run(process_chunks())

    print(f"Done! All chapters saved in '{OUTPUT_FOLDER}'")


if __name__ == "__main__":
    main()
