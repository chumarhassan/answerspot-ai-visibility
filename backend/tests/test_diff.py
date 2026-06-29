"""Tests for the week-over-week diff — the highest-risk logic in the product (§8).

A bug here silently produces wrong "competitor appeared/disappeared" claims, so these
cover the cases most likely to break: first snapshot, no change, new/dropped entrants,
position moves, mention gained/lost, and case/whitespace-insensitive matching.
"""
from datetime import datetime, timedelta, timezone

from diff import SnapshotView, diff_snapshots

T0 = datetime(2026, 6, 1, tzinfo=timezone.utc)
T1 = T0 + timedelta(days=7)


def view(mentioned, position, competitors, ran_at=T1):
    return SnapshotView(ran_at=ran_at, mentioned=mentioned, position=position, competitors=competitors)


def test_first_snapshot_has_no_previous():
    result = diff_snapshots(view(False, None, ["A", "B"]), None)
    assert result.has_previous is False
    assert "First snapshot" in result.summary


def test_no_change_reports_no_change():
    cur = view(True, 2, ["A", "B"])
    prev = view(True, 2, ["A", "B"], ran_at=T0)
    result = diff_snapshots(cur, prev)
    assert result.has_previous is True
    assert result.new_competitors == []
    assert result.dropped_competitors == []
    assert result.position_change == 0
    assert result.summary == "No change since the last check."


def test_new_competitor_detected():
    cur = view(False, None, ["A", "B", "C"])
    prev = view(False, None, ["A", "B"], ran_at=T0)
    result = diff_snapshots(cur, prev)
    assert result.new_competitors == ["C"]
    assert result.dropped_competitors == []
    assert "C" in result.summary


def test_dropped_competitor_detected():
    cur = view(False, None, ["A"])
    prev = view(False, None, ["A", "B"], ran_at=T0)
    result = diff_snapshots(cur, prev)
    assert result.dropped_competitors == ["B"]
    assert result.new_competitors == []


def test_position_improved_is_negative():
    cur = view(True, 1, ["X"])
    prev = view(True, 4, ["X"], ran_at=T0)
    result = diff_snapshots(cur, prev)
    assert result.position_change == -3
    assert "moved up" in result.summary


def test_position_slipped_is_positive():
    cur = view(True, 5, ["X"])
    prev = view(True, 2, ["X"], ran_at=T0)
    result = diff_snapshots(cur, prev)
    assert result.position_change == 3
    assert "slipped" in result.summary


def test_became_mentioned():
    cur = view(True, 3, ["A"])
    prev = view(False, None, ["A", "B"], ran_at=T0)
    result = diff_snapshots(cur, prev)
    assert result.became_mentioned is True
    assert result.lost_mention is False
    assert "started getting recommended" in result.summary


def test_lost_mention():
    cur = view(False, None, ["A", "B"])
    prev = view(True, 1, ["A"], ran_at=T0)
    result = diff_snapshots(cur, prev)
    assert result.lost_mention is True
    assert result.became_mentioned is False
    assert "stopped appearing" in result.summary


def test_position_change_none_when_not_ranked_both_times():
    cur = view(False, None, ["A"])
    prev = view(True, 2, ["A"], ran_at=T0)
    result = diff_snapshots(cur, prev)
    assert result.position_change is None  # not ranked in current


def test_competitor_matching_is_case_and_space_insensitive():
    cur = view(False, None, ["acme  roofing"])
    prev = view(False, None, ["ACME Roofing"], ran_at=T0)
    result = diff_snapshots(cur, prev)
    assert result.new_competitors == []
    assert result.dropped_competitors == []
