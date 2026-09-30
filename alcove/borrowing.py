"""borrowing.py - the counter: issuing, returning and fines.

The house rules are constants so they can be changed in one place.
A loan record looks like:
    {"isbn": "...", "member_id": "M001", "issued": "2025-01-01",
     "due": "2025-01-15", "return_date": None, "fine": 0}
"""

from datetime import timedelta

from alcove import catalog, members
from alcove.utils import LibraryError, format_date, parse_date

LOAN_DAYS = 14      # how long a book may be kept
MAX_LOANS = 3       # books per member at once
FINE_PER_DAY = 2    # rupees per day late


def active_loans(state, member_id):
    """Loans of this member that have not been returned yet."""
    result = []
    for loan in state["loans"]:
        if loan["member_id"] == member_id and loan["return_date"] is None:
            result.append(loan)
    return result


def find_loan(state, member_id, isbn):
    """The member's active loan of this book, or None."""
    for loan in active_loans(state, member_id):
        if loan["isbn"] == isbn:
            return loan
    return None


def calculate_fine(due_text, returned_on):
    """Rs. FINE_PER_DAY for every day after the due date."""
    days_late = (returned_on - parse_date(due_text)).days
    if days_late <= 0:
        return 0
    return days_late * FINE_PER_DAY


def issue_book(state, isbn, member_id, on_date):
    book = catalog.get_book(state, isbn)
    member = members.get_member(state, member_id)

    if member["fines_due"] > 0:
        raise LibraryError("Please pay your fine of Rs. %d first." % member["fines_due"])
    if len(active_loans(state, member["id"])) >= MAX_LOANS:
        raise LibraryError("Limit reached: %d books at a time." % MAX_LOANS)
    if find_loan(state, member["id"], book["isbn"]):
        raise LibraryError("This member already has a copy of this book.")
    if book["copies_available"] < 1:
        raise LibraryError("All copies are out on loan.")

    loan = {
        "isbn": book["isbn"],
        "member_id": member["id"],
        "issued": format_date(on_date),
        "due": format_date(on_date + timedelta(days=LOAN_DAYS)),
        "return_date": None,
        "fine": 0,
    }
    state["loans"].append(loan)
    book["copies_available"] -= 1
    book["times_borrowed"] += 1
    return loan


def return_book(state, isbn, member_id, on_date):
    """Return a book. Gives back the fine (0 if on time)."""
    book = catalog.get_book(state, isbn)
    member = members.get_member(state, member_id)
    loan = find_loan(state, member["id"], book["isbn"])
    if loan is None:
        raise LibraryError("This member has not borrowed that book.")

    loan["return_date"] = format_date(on_date)
    loan["fine"] = calculate_fine(loan["due"], on_date)
    member["fines_due"] += loan["fine"]
    book["copies_available"] += 1
    return loan["fine"]


def pay_fines(state, member_id):
    """Clear the member's fines. Returns the amount paid."""
    member = members.get_member(state, member_id)
    paid = member["fines_due"]
    if paid == 0:
        raise LibraryError("This member has no fines to pay.")
    member["fines_due"] = 0
    return paid
