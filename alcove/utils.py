"""utils.py - input helpers, date helpers and the error type.

Every read_* function keeps asking until the user types something valid,
so the rest of the program never has to deal with bad input.
"""

from datetime import datetime

from alcove import isbn_utils

DATE_FORMAT = "%Y-%m-%d"


class LibraryError(Exception):
    """Raised when a library rule is broken (bad ISBN, no copies left...).

    main.py catches it and prints the message instead of crashing.
    """


def warn(message):
    print("! " + message)


def parse_date(text):
    """Turn 'YYYY-MM-DD' into a date. Raises ValueError if invalid."""
    return datetime.strptime(text, DATE_FORMAT).date()


def format_date(d):
    return d.strftime(DATE_FORMAT)


def read_text(prompt, allow_empty=False):
    """Ask until the user types some text."""
    while True:
        value = input(prompt).strip()
        if value or allow_empty:
            return value
        warn("Please type something.")


def read_int(prompt, minimum, maximum):
    """Ask until the user types a whole number between minimum and maximum."""
    while True:
        try:
            number = int(input(prompt))
        except ValueError:
            warn("That is not a whole number.")
            continue
        if minimum <= number <= maximum:
            return number
        warn("Please enter a number from %d to %d." % (minimum, maximum))


def read_isbn(prompt):
    """Ask until the user types a valid ISBN-13."""
    while True:
        text = input(prompt).strip()
        if isbn_utils.is_valid_isbn(text):
            return isbn_utils.clean(text)
        warn("Invalid ISBN-13 (needs 13 digits and a correct check digit). Try again.")


def confirm(prompt):
    """Ask a yes/no question. Returns True for yes."""
    while True:
        answer = input(prompt + " [y/n]: ").strip().lower()
        if answer == "y":
            return True
        if answer == "n":
            return False
        warn("Please answer y or n.")


def print_table(headers, rows):
    """Print rows as a simple text table."""
    if not rows:
        print("(nothing to show)")
        return
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))
    line = "  ".join("{:<%d}" % w for w in widths)
    print(line.format(*headers))
    print("  ".join("-" * w for w in widths))
    for row in rows:
        print(line.format(*[str(cell) for cell in row]))
