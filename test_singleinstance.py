"""Unit tests for SingleInstance module."""

import unittest
from TPWUtils.SingleInstance import SingleInstance


class TestSingleInstance(unittest.TestCase):
    """Test the SingleInstance class."""

    def test_single_instance_context_manager(self):
        """Test SingleInstance as a context manager."""
        with SingleInstance("test_key_unique_12345") as instance:
            self.assertIsInstance(instance, SingleInstance)

    def test_two_instances_same_key(self):
        """Test that two instances with same key raises RuntimeError."""
        key = "test_duplicate_key_67890"

        with SingleInstance(key):
            # Try to create another instance with same key
            with self.assertRaises(RuntimeError) as context:
                with SingleInstance(key):
                    pass

            self.assertIn("Another instance is already running", str(context.exception))

    def test_sequential_instances_same_key(self):
        """Test that sequential instances with same key work."""
        key = "test_sequential_key_11111"

        # First instance
        with SingleInstance(key):
            pass

        # Second instance after first is released - should work
        with SingleInstance(key):
            pass

    def test_default_key(self):
        """Test that default key uses sys.argv[0]."""
        # Just verify it doesn't crash
        with SingleInstance():
            pass

    def test_enter_returns_self(self):
        """Test that __enter__ returns self."""
        si = SingleInstance("test_return_self_22222")
        result = si.__enter__()
        try:
            self.assertIs(result, si)
        finally:
            si.__exit__(None, None, None)


if __name__ == '__main__':
    unittest.main()
