"""A deliberately small, deterministic recommender for the tutorial catalogue."""

from __future__ import annotations

import copy


def eligible_pairs(facts, *, preferred_only):
    """Propose unread, age-appropriate pairs; GND independently checks the result."""
    users = sorted({row["user"] for row in facts["user_prefers_genre"]})
    books = {row["book"]: row["genre"] for row in facts["book_has_genre"]}
    rated = {(row["user"], row["book"]) for row in facts["user_rated_book"]}
    minors = {row["user"] for row in facts["user_is_minor"]}
    adult = {row["book"] for row in facts["book_rated_adult"]}
    preferences = {(row["user"], row["genre"]) for row in facts["user_prefers_genre"]}
    return [
        {"user": user, "book": book}
        for user in users
        for book in sorted(books)
        if (user, book) not in rated
        and not (user in minors and book in adult)
        and (not preferred_only or (user, books[book]) in preferences)
    ]


def recommend(document, *, user, limit, preferred_only=False):
    """Replace one user's suggestions, preserving all other asserted facts."""
    result = copy.deepcopy(document)
    candidates = eligible_pairs(result["facts"], preferred_only=preferred_only)
    selected = [row for row in candidates if row["user"] == user][:limit]
    result["facts"]["recommendation"] = [
        row for row in result["facts"]["recommendation"] if row["user"] != user
    ] + selected
    return result


def complete(document):
    """Propose exact derived claims and every eligible recommendation for all users."""
    result = copy.deepcopy(document)
    facts = result["facts"]
    facts["book_is_blocked_for"] = [
        {"book": book["book"], "user": user["user"]}
        for book in facts["book_rated_adult"]
        for user in facts["user_is_minor"]
    ]
    pairs = eligible_pairs(facts, preferred_only=True)
    facts["book_is_eligible"] = [{"book": row["book"], "user": row["user"]} for row in pairs]
    facts["recommendation"] = pairs
    result["population"]["covers"] = list(facts)
    return result
