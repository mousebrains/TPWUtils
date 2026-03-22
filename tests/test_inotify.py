"""Unit tests for INotify module."""

import unittest
import queue
import tempfile
import time
from pathlib import Path
from argparse import Namespace
from TPWUtils.INotify import INotify


class TestINotify(unittest.TestCase):
    """Test the INotify class (cross-platform via watchdog)."""

    def test_import(self):
        """Test that INotify can be imported."""
        self.assertIsNotNone(INotify)

    def test_initialization(self):
        """Test INotify initialization."""
        args = Namespace()
        inotify = INotify(args)
        self.assertIsNotNone(inotify.queue)

    def test_add_watch_nonexistent_dir(self):
        """Test that addWatch returns False for nonexistent directory."""
        args = Namespace()
        inotify = INotify(args)
        result = inotify.addWatch("/nonexistent/path/12345")
        self.assertFalse(result)

    def test_add_watch_existing_dir(self):
        """Test that addWatch returns True for existing directory."""
        args = Namespace()
        inotify = INotify(args)
        with tempfile.TemporaryDirectory() as tmpdir:
            result = inotify.addWatch(tmpdir)
            self.assertTrue(result)

    def test_file_creation_event(self):
        """Test that file creation triggers an event."""
        args = Namespace()
        inotify = INotify(args)

        with tempfile.TemporaryDirectory() as tmpdir:
            inotify.addTree(tmpdir)
            inotify.start()
            time.sleep(0.5)  # Let observer settle

            # Create a file
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("hello")

            # Drain events until we find the file-specific one
            found = False
            deadline = time.time() + 5
            while time.time() < deadline:
                try:
                    t0, fn = inotify.queue.get(timeout=0.1)
                    if "test.txt" in fn:
                        found = True
                        self.assertIsInstance(t0, float)
                        break
                except queue.Empty:
                    pass
            self.assertTrue(found, "No event for test.txt received")

    def test_flags_parameter_accepted(self):
        """Test that flags parameter is accepted (for backward compat)."""
        args = Namespace()
        # Should not raise even though flags are ignored with watchdog
        inotify = INotify(args, flags=0x100)
        self.assertIsNotNone(inotify)


if __name__ == "__main__":
    unittest.main()
