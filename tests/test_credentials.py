"""Unit tests for Credentials module."""

import unittest
import os
import stat
import tempfile
import yaml
from unittest.mock import patch
from TPWUtils.Credentials import getCredentials


class TestCredentials(unittest.TestCase):
    """Test the Credentials module."""

    def setUp(self):
        """Create a temporary directory for test files."""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_load_existing_credentials(self):
        """Test loading credentials from an existing file."""
        cred_file = os.path.join(self.test_dir, "test_creds.yaml")

        test_creds = {
            "username": "testuser",
            "password": "testpass"
        }
        with open(cred_file, "w") as f:
            yaml.dump(test_creds, f)

        username, password = getCredentials(cred_file)

        self.assertEqual(username, "testuser")
        self.assertEqual(password, "testpass")

    def test_malformed_file_prompts_user(self):
        """Test that malformed credentials file prompts for new credentials."""
        cred_file = os.path.join(self.test_dir, "bad_creds.yaml")

        # Create a file with missing password
        test_creds = {"username": "testuser"}
        with open(cred_file, "w") as f:
            yaml.dump(test_creds, f)

        with patch("builtins.input", return_value="newuser"), \
             patch("getpass.getpass", return_value="newpass"):
            username, password = getCredentials(cred_file)

        self.assertEqual(username, "newuser")
        self.assertEqual(password, "newpass")

    def test_missing_file_prompts_user(self):
        """Test that missing file prompts for credentials and creates file."""
        cred_file = os.path.join(self.test_dir, "subdir", "new_creds.yaml")

        with patch("builtins.input", return_value="mockuser"), \
             patch("getpass.getpass", return_value="mockpass"):
            username, password = getCredentials(cred_file)

        self.assertEqual(username, "mockuser")
        self.assertEqual(password, "mockpass")
        self.assertTrue(os.path.isfile(cred_file))

    def test_credentials_file_permissions(self):
        """Test that newly created credential files have restricted permissions."""
        cred_file = os.path.join(self.test_dir, "secure_creds.yaml")

        with patch("builtins.input", return_value="user"), \
             patch("getpass.getpass", return_value="pass"):
            getCredentials(cred_file)

        mode = os.stat(cred_file).st_mode
        # Should not be readable by group or others
        self.assertFalse(mode & stat.S_IRGRP)
        self.assertFalse(mode & stat.S_IROTH)
        self.assertFalse(mode & stat.S_IWGRP)
        self.assertFalse(mode & stat.S_IWOTH)

    def test_file_with_expanded_path(self):
        """Test that file paths are properly expanded."""
        cred_file = os.path.join(self.test_dir, "creds.yaml")
        test_creds = {
            "username": "testuser",
            "password": "testpass"
        }
        with open(cred_file, "w") as f:
            yaml.dump(test_creds, f)

        username, password = getCredentials(cred_file)
        self.assertEqual(username, "testuser")


if __name__ == "__main__":
    unittest.main()
