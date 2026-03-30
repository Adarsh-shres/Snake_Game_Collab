# ── self_collision.py ────────────────────────────────────────────────────────
# Lose condition: game ends if the snake's head collides with its own body.


def check_self_collision(head: tuple, body: list[tuple]) -> bool:
    """Return True if the head position overlaps any segment of the body.

    Note: call this *before* inserting the new head into the body list so that
    the head is only compared against existing body segments, not itself.
    """
    return head in body
