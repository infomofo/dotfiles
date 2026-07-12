"""Tests for fetch_threads.py."""
import json
from unittest.mock import MagicMock, patch

import pytest

import fetch_threads


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_run_result(data, returncode=0, stderr=""):
    r = MagicMock()
    r.returncode = returncode
    r.stdout = json.dumps(data)
    r.stderr = stderr
    return r


def make_thread(
    id="T1",
    resolved=False,
    outdated=False,
    path="src/foo.py",
    line=10,
    body="comment body",
    author_login="copilot",
    author_type="Bot",
    extra_comments=None,
):
    comments = [{"path": path, "line": line, "body": body,
                 "author": {"login": author_login, "__typename": author_type}}]
    if extra_comments:
        comments.extend(extra_comments)
    return {"id": id, "isResolved": resolved, "isOutdated": outdated,
            "comments": {"nodes": comments}}


# ---------------------------------------------------------------------------
# run()
# ---------------------------------------------------------------------------

class TestRun:
    def test_returns_parsed_json(self):
        with patch("subprocess.run", return_value=make_run_result({"k": "v"})):
            assert fetch_threads.run(["gh", "test"]) == {"k": "v"}

    def test_exits_on_nonzero_returncode(self):
        with patch("subprocess.run", return_value=make_run_result({}, returncode=1, stderr="oops")):
            with pytest.raises(SystemExit):
                fetch_threads.run(["gh", "test"])

    def test_exits_on_invalid_json(self):
        r = MagicMock()
        r.returncode = 0
        r.stdout = "not json"
        with patch("subprocess.run", return_value=r):
            with pytest.raises(SystemExit):
                fetch_threads.run(["gh", "test"])


# ---------------------------------------------------------------------------
# fetch_deleted_paths()
# ---------------------------------------------------------------------------

class TestFetchDeletedPaths:
    def test_returns_removed_filenames(self):
        files = [
            {"filename": "old.py", "status": "removed"},
            {"filename": "kept.py", "status": "modified"},
        ]
        with patch("fetch_threads.run", return_value=files):
            result = fetch_threads.fetch_deleted_paths("o", "r", 1)
        assert result == {"old.py"}

    def test_paginates_until_short_page(self):
        page1 = [{"filename": f"f{i}.py", "status": "removed"} for i in range(100)]
        page2 = [{"filename": "last.py", "status": "removed"}]
        with patch("fetch_threads.run", side_effect=[page1, page2]):
            result = fetch_threads.fetch_deleted_paths("o", "r", 1)
        assert len(result) == 101

    def test_skips_entries_without_filename(self):
        files = [{"status": "removed"}, {"filename": "real.py", "status": "removed"}]
        with patch("fetch_threads.run", return_value=files):
            result = fetch_threads.fetch_deleted_paths("o", "r", 1)
        assert result == {"real.py"}


# ---------------------------------------------------------------------------
# fetch_threads()
# ---------------------------------------------------------------------------

def make_graphql_page(threads, has_next=False, cursor="cur1"):
    return {
        "data": {
            "repository": {
                "pullRequest": {
                    "reviewThreads": {
                        "pageInfo": {"hasNextPage": has_next, "endCursor": cursor},
                        "nodes": threads,
                    }
                }
            }
        }
    }


class TestFetchThreads:
    def test_returns_threads(self):
        page = make_graphql_page([make_thread()])
        with patch("fetch_threads.run", return_value=page):
            result = fetch_threads.fetch_threads("o", "r", 1)
        assert len(result) == 1

    def test_paginates(self):
        page1 = make_graphql_page([make_thread(id="T1")], has_next=True, cursor="c1")
        page2 = make_graphql_page([make_thread(id="T2")], has_next=False)
        with patch("fetch_threads.run", side_effect=[page1, page2]):
            result = fetch_threads.fetch_threads("o", "r", 1)
        assert len(result) == 2

    def test_exits_on_graphql_errors(self):
        with patch("fetch_threads.run", return_value={"errors": [{"message": "bad"}]}):
            with pytest.raises(SystemExit):
                fetch_threads.fetch_threads("o", "r", 1)

    def test_exits_when_pr_not_found(self):
        with patch("fetch_threads.run", return_value={"data": {"repository": {"pullRequest": None}}}):
            with pytest.raises(SystemExit):
                fetch_threads.fetch_threads("o", "r", 1)


# ---------------------------------------------------------------------------
# print_threads()
# ---------------------------------------------------------------------------

class TestPrintThreads:
    def test_prints_open_thread(self, capsys):
        fetch_threads.print_threads([make_thread()], set())
        out = capsys.readouterr().out
        assert "[copilot / Bot] src/foo.py:10 thread:T1" in out
        assert "comment body" in out

    def test_skips_resolved(self, capsys):
        fetch_threads.print_threads([make_thread(resolved=True)], set())
        assert capsys.readouterr().out == ""

    def test_skips_outdated(self, capsys):
        fetch_threads.print_threads([make_thread(outdated=True)], set())
        assert capsys.readouterr().out == ""

    def test_skips_deleted_path(self, capsys):
        fetch_threads.print_threads([make_thread(path="gone.py")], {"gone.py"})
        assert capsys.readouterr().out == ""

    def test_skips_none_thread(self, capsys):
        fetch_threads.print_threads([None], set())
        assert capsys.readouterr().out == ""

    def test_truncates_body_at_300(self, capsys):
        fetch_threads.print_threads([make_thread(body="x" * 400)], set())
        out = capsys.readouterr().out
        assert "x" * 300 in out
        assert "x" * 301 not in out

    def test_human_reply_shown(self, capsys):
        reply = {"path": "src/foo.py", "line": 10, "body": "looks fine",
                 "author": {"login": "will", "__typename": "User"}}
        fetch_threads.print_threads([make_thread(extra_comments=[reply])], set())
        out = capsys.readouterr().out
        assert "1 HUMAN REPLY" in out
        assert "[will]: looks fine" in out

    def test_bot_reply_not_shown_as_human(self, capsys):
        reply = {"path": "src/foo.py", "line": 10, "body": "bot follow-up",
                 "author": {"login": "copilot", "__typename": "Bot"}}
        fetch_threads.print_threads([make_thread(extra_comments=[reply])], set())
        assert "HUMAN REPLY" not in capsys.readouterr().out

    def test_multiple_human_replies(self, capsys):
        replies = [
            {"path": "f.py", "line": 1, "body": "reply one",
             "author": {"login": "alice", "__typename": "User"}},
            {"path": "f.py", "line": 1, "body": "reply two",
             "author": {"login": "bob", "__typename": "User"}},
        ]
        fetch_threads.print_threads([make_thread(extra_comments=replies)], set())
        out = capsys.readouterr().out
        assert "2 HUMAN REPLY" in out
        assert "[alice]: reply one" in out
        assert "[bob]: reply two" in out

    def test_missing_author_defaults_to_unknown(self, capsys):
        t = make_thread()
        t["comments"]["nodes"][0]["author"] = None
        fetch_threads.print_threads([t], set())
        assert "unknown / unknown" in capsys.readouterr().out
