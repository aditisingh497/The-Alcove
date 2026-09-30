"""members.py - registering and managing library members.

Member IDs are simple and readable: M001, M002, M003 ...
A member record looks like:
    {"id": "M001", "name": "Asha", "fines_due": 0}
"""

from alcove.utils import LibraryError


def add_member(state, name):
    if not name.strip():
        raise LibraryError("A member needs a name.")
    member_id = "M%03d" % state["next_member_id"]
    state["next_member_id"] += 1
    member = {"id": member_id, "name": name.strip().title(), "fines_due": 0}
    state["members"][member_id] = member
    return member


def get_member(state, member_id):
    member_id = member_id.strip().upper()
    if member_id not in state["members"]:
        raise LibraryError("No member with ID %s." % member_id)
    return state["members"][member_id]


def remove_member(state, member_id):
    member = get_member(state, member_id)
    for loan in state["loans"]:
        if loan["member_id"] == member["id"] and loan["return_date"] is None:
            raise LibraryError("Member still has books on loan.")
    if member["fines_due"] > 0:
        raise LibraryError("Member still owes Rs. %d in fines." % member["fines_due"])
    del state["members"][member["id"]]


def list_members(state):
    """All members, sorted by name."""
    return sorted(state["members"].values(), key=lambda m: m["name"])
