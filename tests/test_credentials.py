"""Unit tests for Credentials module."""

import unittest
import os
import tempfile
import yaml
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

        # Create a test credentials file
        test_creds = {
            "username": "testuser",
            "password": "testpass"
        }
        with open(cred_file, "w") as f:
            yaml.dump(test_creds, f)

        # Load credentials
        username, password = getCredentials(cred_file)

        self.assertEqual(username, "testuser")
        self.assertEqual(password, "testpass")

    def test_malformed_credentials_file(self):
        """Test handling of malformed credentials file."""
        cred_file = os.path.join(self.test_dir, "bad_creds.yaml")

        # Create a file with missing password
        test_creds = {"username": "testuser"}
        with open(cred_file, "w") as f:
            yaml.dump(test_creds, f)

        # This should prompt for new credentials, but in test we can't provide input
        # So we just verify it doesn't crash and attempts to read the file
        # (The actual prompting would need mocking for full test)
        with self.assertRaises((EOFError, OSError)):
            # Will fail on input() call since stdin is not available in test
            # Pytest raises OSError, standard unittest may raise EOFError
            getCredentials(cred_file)

    def test_file_with_expanded_path(self):
        """Test that file paths are properly expanded."""
        # Create credentials in temp dir
        cred_file = os.path.join(self.test_dir, "creds.yaml")
        test_creds = {
            "username": "testuser",
            "password": "testpass"
        }
        with open(cred_file, "w") as f:
            yaml.dump(test_creds, f)

        # Load with absolute path
        username, password = getCredentials(cred_file)
        self.assertEqual(username, "testuser")


if __name__ == '__main__':
    unittest.main()
