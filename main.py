"""main.py - The Alcove: a small library manager. Run with:  python main.py

This file only talks to the user (menus and prompts).
The real work is done by the modules in the alcove/ folder.
"""

from datetime import date

from alcove import borrowing, catalog, insights, members, storage
from alcove.utils import (LibraryError, confirm, format_date, parse_date,
                          print_table, read_int, read_isbn, read_text, warn)

DATA_FILE = storage.DATA_FILE

SAMPLE_BOOKS = [
    ("9780743273565", "The Great Gatsby", "F. Scott Fitzgerald", "Classic", 2),
    ("9780451524935", "1984", "George Orwell", "Dystopian", 3),
    ("9780141439518", "Pride and Prejudice", "Jane Austen", "Romance", 2),
    ("9780547928227", "The Hobbit", "J. R. R. Tolkien", "Fantasy", 2),
    ("9780441172719", "Dune", "Frank Herbert", "Science Fiction", 1),
    ("9780062315007", "The Alchemist", "Paulo Coelho", "Fiction", 2),
]


def load_sample_data(state):
    for isbn, title, author, genre, copies in SAMPLE_BOOKS:
        catalog.add_book(state, isbn, title, author, genre, copies)
    for name in ("Aarav Mehta", "Diya Nair", "Kabir Rao"):
        members.add_member(state, name)


def show_menu(title, options, last="Back"):
    """Print a numbered menu and return the user's choice (0 = last)."""
    print("\n=== %s ===" % title)
    for number, text in enumerate(options, start=1):
        print("%d. %s" % (number, text))
    print("0. %s" % last)
    return read_int("Your choice: ", 0, len(options))


def show_books(book_list):
    rows = []
    for b in book_list:
        rows.append((b["isbn"], b["title"], b["author"], b["genre"],
                     "%d/%d" % (b["copies_available"], b["copies_total"])))
    print_table(["ISBN", "Title", "Author", "Genre", "In/Total"], rows)


# ------------------------------------------------------------------ books
def menu_books(state):
    choice = show_menu("Books", ["View all books", "Add a book",
                                 "Search by keyword", "Update a book",
                                 "Remove a book"])
    if choice == 1:
        show_books(sorted(state["books"].values(), key=lambda b: b["title"]))
    elif choice == 2:
        isbn = read_isbn("ISBN-13: ")
        title = read_text("Title: ")
        author = read_text("Author: ")
        genre = read_text("Genre (optional): ", allow_empty=True)
        copies = read_int("Number of copies (1-50): ", 1, 50)
        catalog.add_book(state, isbn, title, author, genre, copies)
        print("Book added.")
    elif choice == 3:
        show_books(catalog.search_books(state, read_text("Search for: ")))
    elif choice == 4:
        isbn = read_isbn("ISBN of the book to update: ")
        catalog.get_book(state, isbn)            # make sure it exists
        print("Leave a field blank to keep it as it is.")
        title = read_text("New title: ", allow_empty=True)
        author = read_text("New author: ", allow_empty=True)
        genre = read_text("New genre: ", allow_empty=True)
        catalog.update_book(state, isbn, title, author, genre)
        print("Book updated.")
    elif choice == 5:
        isbn = read_isbn("ISBN of the book to remove: ")
        book = catalog.get_book(state, isbn)
        if confirm("Remove '%s'?" % book["title"]):
            catalog.remove_book(state, isbn)
            print("Book removed.")


# ---------------------------------------------------------------- members
def menu_members(state):
    choice = show_menu("Members", ["List members", "Add a member",
                                   "View a member's loans", "Remove a member"])
    if choice == 1:
        rows = []
        for m in members.list_members(state):
            rows.append((m["id"], m["name"], "Rs. %d" % m["fines_due"]))
        print_table(["ID", "Name", "Fines due"], rows)
    elif choice == 2:
        member = members.add_member(state, read_text("Name: "))
        print("Welcome, %s! Your member ID is %s." % (member["name"], member["id"]))
    elif choice == 3:
        member = members.get_member(state, read_text("Member ID: "))
        print("%s | fines due: Rs. %d" % (member["name"], member["fines_due"]))
        rows = []
        for loan in borrowing.active_loans(state, member["id"]):
            title = state["books"][loan["isbn"]]["title"]
            rows.append((title, loan["issued"], loan["due"]))
        print_table(["Title", "Issued", "Due"], rows)
    elif choice == 4:
        member = members.get_member(state, read_text("Member ID: "))
        if confirm("Remove %s?" % member["name"]):
            members.remove_member(state, member["id"])
            print("Member removed.")


# ---------------------------------------------------------------- counter
def menu_counter(state, today):
    choice = show_menu("Counter (date: %s)" % format_date(today),
                       ["Issue a book", "Return a book", "Pay a fine"])
    if choice == 0:
        return
    member_id = read_text("Member ID: ")
    if choice == 3:
        paid = borrowing.pay_fines(state, member_id)
        print("Paid Rs. %d. Thank you." % paid)
        return

    isbn = read_isbn("ISBN-13: ")
    if choice == 1:
        loan = borrowing.issue_book(state, isbn, member_id, today)
        print("Book issued. Due back on %s." % loan["due"])
    elif choice == 2:
        fine = borrowing.return_book(state, isbn, member_id, today)
        print("Book returned.")
        if fine > 0:
            print("Late fine: Rs. %d added to the member's account." % fine)


# ---------------------------------------------------------------- reports
def menu_reports(state, today):
    choice = show_menu("Reports", ["Library summary", "Most popular books (top K)",
                                   "Overdue books", "Books per genre"])
    if choice == 1:
        for label, value in insights.summary(state).items():
            print("%-20s %s" % (label, value))
    elif choice == 2:
        k = read_int("How many books (K)? ", 1, 20)
        print_table(["Title", "Times borrowed"], insights.top_k_books(state, k))
    elif choice == 3:
        print_table(["Member", "Title", "Days late", "Fine so far"],
                    insights.overdue_report(state, today))
    elif choice == 4:
        print_table(["Genre", "Titles"], sorted(insights.count_by_genre(state).items()))


# ------------------------------------------------------------- main loop
def run():
    state = storage.load_state(DATA_FILE)
    if not state["books"]:
        load_sample_data(state)
        storage.save_state(state, DATA_FILE)
        print("(Sample books and members have been added for you.)")

    today = date.today()
    print("\nWelcome to The Alcove - a small library manager")

    while True:
        choice = show_menu("Main menu (date: %s)" % format_date(today),
                           ["Books", "Members", "Counter (issue / return / fines)",
                            "Reports", "Change today's date (for demos)"],
                           last="Exit")
        if choice == 0:
            print("Goodbye!")
            return
        try:
            if choice == 1:
                menu_books(state)
            elif choice == 2:
                menu_members(state)
            elif choice == 3:
                menu_counter(state, today)
            elif choice == 4:
                menu_reports(state, today)
            elif choice == 5:
                today = parse_date(read_text("New date (YYYY-MM-DD): "))
            storage.save_state(state, DATA_FILE)
        except LibraryError as problem:
            warn(str(problem))
        except ValueError:
            warn("That date is not valid. Use YYYY-MM-DD.")


if __name__ == "__main__":
    try:
        run()
    except (KeyboardInterrupt, EOFError):
        print("\nGoodbye! (data is saved after every action)")
