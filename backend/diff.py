"""Week-over-week snapshot diffing.

This is the highest-risk logic in the product: a bug here silently produces wrong
"competitor appeared/disappeared" claims (§8). It is therefore kept PURE — it takes
two plain snapshot-like inputs and returns a plain result, no DB or network — so it
can be exhaustively unit-tested (see tests/test_diff.py).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class SnapshotView:
    """Minimal, hashable view of a snapshot for diffing."""

    ran_at: datetime
    mentioned: bool
    position: int | None
    competitors: list[str]


@dataclass
class DiffResult:
    has_previous: bool
    current_ran_at: datetime | None = None
    previous_ran_at: datetime | None = None
    position_change: int | None = None  # negative = improved (moved up the list)
    new_competitors: list[str] = field(default_factory=list)
    dropped_competitors: list[str] = field(default_factory=list)
    became_mentioned: bool = False
    lost_mention: bool = False
    summary: str = ""


def _norm(name: str) -> str:
    """Normalize a competitor name for set comparison (case/space-insensitive)."""
    return " ".join(name.lower().split())


def diff_snapshots(current: SnapshotView, previous: SnapshotView | None) -> DiffResult:
    """Compare the current snapshot to the previous one.

    `previous` is None for a business's very first snapshot — in that case there is
    nothing to diff against and has_previous is False.
    """
    if previous is None:
        return DiffResult(
            has_previous=False,
            current_ran_at=current.ran_at,
            summary="First snapshot recorded — week-over-week changes will appear here next check.",
        )

    # Compare competitor sets on normalized names, but report the current-cased name.
    prev_norms = {_norm(c) for c in previous.competitors}
    cur_norms = {_norm(c) for c in current.competitors}

    new_competitors = [c for c in current.competitors if _norm(c) not in prev_norms]
    dropped_competitors = [c for c in previous.competitors if _norm(c) not in cur_norms]

    # Position change only meaningful when ranked in BOTH snapshots.
    position_change: int | None = None
    if current.position is not None and previous.position is not None:
        position_change = current.position - previous.position

    became_mentioned = current.mentioned and not previous.mentioned
    lost_mention = previous.mentioned and not current.mentioned

    return DiffResult(
        has_previous=True,
        current_ran_at=current.ran_at,
        previous_ran_at=previous.ran_at,
        position_change=position_change,
        new_competitors=new_competitors,
        dropped_competitors=dropped_competitors,
        became_mentioned=became_mentioned,
        lost_mention=lost_mention,
        summary=_summarize(
            position_change, new_competitors, dropped_competitors, became_mentioned, lost_mention
        ),
    )


def _summarize(
    position_change: int | None,
    new_competitors: list[str],
    dropped_competitors: list[str],
    became_mentioned: bool,
    lost_mention: bool,
) -> str:
    parts: list[str] = []

    if became_mentioned:
        parts.append("You started getting recommended by AI this week.")
    elif lost_mention:
        parts.append("You stopped appearing in AI recommendations this week.")

    if position_change is not None and position_change != 0:
        if position_change < 0:
            parts.append(f"You moved up {abs(position_change)} place(s) in the recommendation list.")
        else:
            parts.append(f"You slipped down {position_change} place(s) in the recommendation list.")

    if new_competitors:
        parts.append(f"New competitor(s) now recommended: {', '.join(new_competitors)}.")
    if dropped_competitors:
        parts.append(f"No longer recommended: {', '.join(dropped_competitors)}.")

    if not parts:
        return "No change since the last check."
    return " ".join(parts)
