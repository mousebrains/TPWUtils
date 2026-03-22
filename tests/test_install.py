"""Unit tests for install module."""

import unittest
import os
import tempfile
from unittest.mock import patch
from argparse import ArgumentParser, Namespace
from TPWUtils.install import (
    stripComments, needsToBeCopied,
    mkSystemctl, addArgs,
)


class TestStripComments(unittest.TestCase):
    """Test the stripComments function."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_strips_inline_comments(self):
        path = os.path.join(self.test_dir, "test.txt")
        with open(path, "w") as f:
            f.write("line1 # comment\n")
            f.write("# full comment\n")
            f.write("line2\n")
        result = stripComments(path)
        self.assertEqual(result, "line1\nline2")

    def test_all_comments(self):
        path = os.path.join(self.test_dir, "test.txt")
        with open(path, "w") as f:
            f.write("# only comments\n")
            f.write("# another comment\n")
        result = stripComments(path)
        self.assertEqual(result, "")

    def test_no_comments(self):
        path = os.path.join(self.test_dir, "test.txt")
        with open(path, "w") as f:
            f.write("line1\nline2\n")
        result = stripComments(path)
        self.assertEqual(result, "line1\nline2")


class TestNeedsToBeCopied(unittest.TestCase):
    """Test the needsToBeCopied function."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_new_file_needs_copy(self):
        src = os.path.join(self.test_dir, "test.service")
        with open(src, "w") as f:
            f.write("content")
        dest_dir = os.path.join(self.test_dir, "dest")
        args = Namespace(serviceDirectory=dest_dir, force=False)
        result = needsToBeCopied(src, args)
        self.assertIsNotNone(result)

    def test_identical_files_skip(self):
        src_dir = os.path.join(self.test_dir, "src")
        dest_dir = os.path.join(self.test_dir, "dest")
        os.makedirs(src_dir)
        os.makedirs(dest_dir)
        src = os.path.join(src_dir, "test.service")
        content = "some content\n"
        with open(src, "w") as f:
            f.write(content)
        with open(os.path.join(dest_dir, "test.service"), "w") as f:
            f.write(content)
        args = Namespace(serviceDirectory=dest_dir, force=False)
        result = needsToBeCopied(src, args)
        self.assertIsNone(result)

    def test_force_flag_overrides(self):
        src_dir = os.path.join(self.test_dir, "src")
        dest_dir = os.path.join(self.test_dir, "dest")
        os.makedirs(src_dir)
        os.makedirs(dest_dir)
        src = os.path.join(src_dir, "test.service")
        content = "same content\n"
        with open(src, "w") as f:
            f.write(content)
        with open(os.path.join(dest_dir, "test.service"), "w") as f:
            f.write(content)
        args = Namespace(serviceDirectory=dest_dir, force=True)
        result = needsToBeCopied(src, args)
        self.assertIsNotNone(result)


class TestMkSystemctl(unittest.TestCase):
    """Test the mkSystemctl function."""

    @patch("subprocess.run")
    def test_system_mode(self, mock_run):
        args = Namespace(user=False, sudo="sudo", systemctl="systemctl", dryrun=False)
        mkSystemctl(args, ("status",), {"test.service"})
        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]
        self.assertEqual(cmd[0], "sudo")
        self.assertEqual(cmd[1], "systemctl")

    @patch("subprocess.run")
    def test_user_mode(self, mock_run):
        args = Namespace(user=True, systemctl="systemctl", dryrun=False)
        mkSystemctl(args, ("status",), {"test.service"})
        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]
        self.assertEqual(cmd[0], "systemctl")
        self.assertIn("--user", cmd)

    @patch("subprocess.run")
    def test_dryrun_skips_execution(self, mock_run):
        args = Namespace(user=True, systemctl="systemctl", dryrun=True)
        mkSystemctl(args, ("status",))
        mock_run.assert_not_called()


class TestAddArgs(unittest.TestCase):
    """Test the addArgs function."""

    def test_adds_expected_args(self):
        parser = ArgumentParser()
        addArgs(parser)
        args = parser.parse_args(["--service", "test.service", "--install"])
        self.assertTrue(args.install)
        self.assertIn("test.service", args.service)

    def test_uses_bare_command_names(self):
        parser = ArgumentParser()
        addArgs(parser)
        args = parser.parse_args(["--service", "test.service"])
        self.assertEqual(args.sudo, "sudo")
        self.assertEqual(args.systemctl, "systemctl")
        self.assertEqual(args.mkdir, "mkdir")
        self.assertEqual(args.cp, "cp")
        self.assertEqual(args.rm, "rm")


if __name__ == "__main__":
    unittest.main()
