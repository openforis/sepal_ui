"""Scratch directories must land on local disk on SEPAL, where /tmp is NFS."""

import tempfile
from pathlib import Path

from pysepal.scripts import scratch


class TestOnSepal:
    def test_true_only_for_the_platform_value(self, monkeypatch):
        monkeypatch.setenv("SEPAL", "true")
        assert scratch.on_sepal() is True

    def test_tolerates_case_and_whitespace(self, monkeypatch):
        monkeypatch.setenv("SEPAL", " True\n")
        assert scratch.on_sepal() is True

    def test_false_when_unset(self, monkeypatch):
        monkeypatch.delenv("SEPAL", raising=False)
        assert scratch.on_sepal() is False

    def test_false_for_other_values(self, monkeypatch):
        monkeypatch.setenv("SEPAL", "false")
        assert scratch.on_sepal() is False


class TestScratchRoot:
    def test_stdlib_default_off_sepal(self, monkeypatch):
        monkeypatch.delenv("SEPAL", raising=False)

        assert scratch.scratch_root() == Path(tempfile.gettempdir())

    def test_local_disk_on_sepal(self, monkeypatch):
        monkeypatch.setenv("SEPAL", "true")
        monkeypatch.setattr(scratch.os, "access", lambda *_: True)

        assert scratch.scratch_root() == scratch.SEPAL_SCRATCH_DIR

    def test_falls_back_when_the_sepal_path_is_not_writable(self, monkeypatch):
        monkeypatch.setenv("SEPAL", "true")
        monkeypatch.setattr(scratch.os, "access", lambda *_: False)

        assert scratch.scratch_root() == Path(tempfile.gettempdir())

    def test_tmpdir_does_not_override_the_local_disk(self, monkeypatch, tmp_path):
        """TMPDIR says where to put temp files, not that the location is fast."""
        monkeypatch.setenv("SEPAL", "true")
        monkeypatch.setenv("TMPDIR", str(tmp_path))
        monkeypatch.setattr(scratch.os, "access", lambda *_: True)

        assert scratch.scratch_root() == scratch.SEPAL_SCRATCH_DIR


class TestScratchDir:
    def test_creates_a_new_directory_under_the_root(self, monkeypatch, tmp_path):
        monkeypatch.setattr(scratch, "scratch_root", lambda: tmp_path)

        created = scratch.scratch_dir(prefix="probe_")

        assert created.is_dir()
        assert created.parent == tmp_path
        assert created.name.startswith("probe_")

    def test_each_call_is_a_distinct_directory(self, monkeypatch, tmp_path):
        monkeypatch.setattr(scratch, "scratch_root", lambda: tmp_path)

        assert scratch.scratch_dir() != scratch.scratch_dir()

    def test_creates_a_missing_root(self, monkeypatch, tmp_path):
        root = tmp_path / "not" / "there" / "yet"
        monkeypatch.setattr(scratch, "scratch_root", lambda: root)

        assert scratch.scratch_dir().parent == root
