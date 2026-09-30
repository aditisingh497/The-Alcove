"""isbn_utils.py - ISBN-13 check-digit validation.

The last digit of an ISBN-13 is a check digit. Digits are weighted
1, 3, 1, 3, ... and the total (including the check digit) must be
divisible by 10. We use this to reject typing mistakes.
"""


def clean(text):
    """Remove hyphens and spaces from an ISBN."""
    return text.replace("-", "").replace(" ", "")


def is_valid_isbn(text):
    """True if text is a valid ISBN-13."""
    code = clean(text)
    if len(code) != 13 or not (code.isascii() and code.isdigit()):
        return False

    total = 0
    for position in range(13):
        weight = 1 if position % 2 == 0 else 3
        total += int(code[position]) * weight
    return total % 10 == 0
