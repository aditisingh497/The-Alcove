"""catalog.py - the shelves: adding, finding and changing books.

A book record looks like:
    {"isbn": "...", "title": "...", "author": "...", "genre": "...",
     "copies_total": 2, "copies_available": 1, "times_borrowed": 5}
"""

from alcove import isbn_utils
from alcove.utils import LibraryError


def add_book(state, isbn, title, author, genre, copies):
    if not isbn_utils.is_valid_isbn(isbn):
        raise LibraryError("Invalid ISBN (needs 13 digits and a correct check digit).")
    isbn = isbn_utils.clean(isbn)
    if isbn in state["books"]:
        raise LibraryError("A book with this ISBN already exists.")
    if not title.strip() or not author.strip():
        raise LibraryError("Title and author cannot be blank.")
    if copies < 1:
        raise LibraryError("A book needs at least one copy.")

    book = {
        "isbn": isbn,
        "title": title.strip(),
        "author": author.strip(),
        "genre": genre.strip().title() or "General",
        "copies_total": copies,
        "copies_available": copies,
        "times_borrowed": 0,
    }
    state["books"][isbn] = book
    return book


def get_book(state, isbn):
    isbn = isbn_utils.clean(isbn)
    if isbn not in state["books"]:
        raise LibraryError("No book with ISBN %s." % isbn)
    return state["books"][isbn]


def update_book(state, isbn, title, author, genre):
    """Change the given fields. A blank value keeps the old one."""
    book = get_book(state, isbn)
    if title.strip():
        book["title"] = title.strip()
    if author.strip():
        book["author"] = author.strip()
    if genre.strip():
        book["genre"] = genre.strip().title()
    return book


def remove_book(state, isbn):
    book = get_book(state, isbn)
    if book["copies_available"] != book["copies_total"]:
        raise LibraryError("Some copies are still on loan.")
    del state["books"][book["isbn"]]


def search_books(state, keyword):
    """Books whose title, author or genre contains the keyword."""
    keyword = keyword.strip().lower()
    found = []
    for book in state["books"].values():
        text = book["title"] + " " + book["author"] + " " + book["genre"]
        if keyword != "" and keyword in text.lower():
            found.append(book)
    return found
