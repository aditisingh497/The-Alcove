"""insights.py - reports built from the library data."""

from alcove.borrowing import FINE_PER_DAY
from alcove.utils import parse_date


def top_k_books(state, k):
    """The k most-borrowed books as (title, times_borrowed) pairs."""
    ranked = sorted(state["books"].values(),
                    key=lambda book: book["times_borrowed"], reverse=True)
    result = []
    for book in ranked[:k]:
        result.append((book["title"], book["times_borrowed"]))
    return result


def overdue_report(state, on_date):
    """Rows of (member name, title, days late, fine so far)."""
    rows = []
    for loan in state["loans"]:
        if loan["return_date"] is not None:
            continue
        days_late = (on_date - parse_date(loan["due"])).days
        if days_late > 0:
            name = state["members"][loan["member_id"]]["name"]
            title = state["books"][loan["isbn"]]["title"]
            rows.append((name, title, days_late, days_late * FINE_PER_DAY))
    return rows


def count_by_genre(state):
    """Dictionary of genre -> number of titles."""
    counts = {}
    for book in state["books"].values():
        genre = book["genre"]
        counts[genre] = counts.get(genre, 0) + 1
    return counts


def summary(state):
    """Headline numbers for the front desk."""
    total_copies = 0
    available = 0
    for book in state["books"].values():
        total_copies += book["copies_total"]
        available += book["copies_available"]
    fines = 0
    for member in state["members"].values():
        fines += member["fines_due"]
    return {
        "Titles": len(state["books"]),
        "Copies": total_copies,
        "Copies on loan": total_copies - available,
        "Members": len(state["members"]),
        "Fines outstanding": "Rs. %d" % fines,
    }
