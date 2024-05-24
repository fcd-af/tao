"""Script to send random Tao Te Ching quotes to slack."""

import argparse
import os
import random
import sys
from pathlib import Path

import requests

BOOK_TYPE = dict[str, dict[str, list[str]]]


def parse_book(path: Path) -> BOOK_TYPE:
    """Parse the Tao Te Ching markdown file into a dictionary.

    Args:
        path (Path): Path to the Tao Te Ching markdown file

    Returns:
        BOOK_TYPE: The Tao Te Ching book as a dictionary
    """
    with open(path) as f:
        lines: list[str] = f.readlines()

    book: BOOK_TYPE = {}

    section: str | None = None
    chapter: str | None = None
    phrase: list[str] = []

    for line in lines:
        if line.startswith("## "):
            # section header (section 1 or 2)
            section = line.lstrip("#").strip()
            # print(f"section: {section}")
            if section not in book:
                book[section] = {}
                chapter = None
                phrase = []
            else:
                print(f"Error: duplicate section {section}")
                sys.exit(1)
        elif section and line.startswith("### "):
            # chapter header
            chapter = line.lstrip("#").strip()
            # print(f"chapter: {chapter}")
            if chapter not in book[section]:
                book[section][chapter] = []
            else:
                print(f"Error: duplicate chapter {chapter}")
                sys.exit(1)
        elif section and chapter:
            if line.strip():
                phrase.append(line.strip())
            elif phrase:
                book[section][chapter].append("\n".join(phrase))
                phrase = []

    return book


def random_phrase(book: BOOK_TYPE) -> tuple[str, str]:
    """Select a random phrase from the Tao Te Ching book.

    Args:
        book (BOOK_TYPE): The Tao Te Ching book as a dictionary

    Returns:
        tuple[str, str]: The section and phrase
    """
    section = random.choice(list(book.keys()))
    chapter = random.choice(list(book[section].keys()))
    # phrase = random.choice(book[section][chapter])
    return (f"{section} - Chapter {chapter}", "\n\n".join(book[section][chapter]))


def main() -> None:
    """Main function.

    Parses arguments, parses the book, selects a random phrase and sends it to slack.
    """
    parser = argparse.ArgumentParser(description="Read the tao te ching in markdown format")
    parser.add_argument("path", type=str, help="path to tao te ching markdown file")

    args = parser.parse_args()

    path_raw = args.path
    path = Path(path_raw).resolve()

    if not path.exists():
        print(f"Error: {path} not found")
        sys.exit(1)

    book = parse_book(path)

    title, message = random_phrase(book)

    # send to slack
    webhook: str | None = os.getenv("SLACK_WEBHOOK")

    if not webhook:
        print("Error: SLACK_WEBHOOK environment variable not set")
        sys.exit(1)

    res = requests.post(webhook, json={"title": title, "message": message})

    if not res.ok:
        print(f"Error: {res.status_code} - {res.text}")
        sys.exit(1)
    else:
        print("Message sent")


if __name__ == "__main__":
    main()
