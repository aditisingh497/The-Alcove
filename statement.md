# Problem Statement — The Alcove

## Problem statement
Small community libraries — a hostel reading corner, a club shelf, a cafe with a
bookcase — are usually run from a paper register or a spreadsheet. This causes
familiar problems: typing mistakes in ISBNs, fines worked out by hand, and no
idea which books are actually popular. Full library software is too heavy for
such places.

**The Alcove** is a small, menu-driven library manager that checks its own data,
enforces simple borrowing rules, and reports on the borrowing history — all in
plain Python with no database or internet needed.

## Scope of the project
**In scope**
- Book management (add, view, search, update, remove) with ISBN-13 check-digit validation
- Member management (add, list, view loans, remove)
- Issuing and returning books, due dates, automatic late fines, fine payment
- Reports: library summary, most popular books, overdue list, books per genre
- Data saved in a JSON file

**Out of scope**
- Graphical or web interface, multi-user access, real payments, barcode
  scanning, e-mail/SMS notifications, waitlists, renewals, recommendations.

## Target users
- **The librarian** of a small library who runs the daily checkouts.
- **First-year programming students**, who can read the code as an example of
  functions, lists, dictionaries, modules and file handling.

## Features
1. **Books** – add, view, search by keyword, update, remove; ISBN-13 validation
2. **Members** – add, list, view a member's loans, remove; IDs like `M001`
3. **Counter** – issue (14 days), return, fine of Rs. 2 per late day, 3-book limit,
   unpaid fines block new loans
4. **Reports** – summary, top-K most borrowed books, overdue books, genre counts
5. **Reliability** – every input is validated, friendly error messages, data saved automatically
