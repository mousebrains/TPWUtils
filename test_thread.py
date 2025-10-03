"""Unit tests for Thread module."""

import unittest
import time
from argparse import Namespace
from TPWUtils.Thread import Thread


class TestThread(unittest.TestCase):
    """Test the Thread class."""

    def test_thread_initialization(self):
        """Test thread can be initialized."""
        class DummyThread(Thread):
            def runIt(self):
                pass

        args = Namespace()
        t = DummyThread("test", args)
        self.assertEqual(t.name, "test")
        self.assertEqual(t.args, args)

    def test_thread_no_args(self):
        """Test thread can be initialized without args."""
        class DummyThread(Thread):
            def runIt(self):
                pass

        t = DummyThread("test")
        self.assertEqual(t.name, "test")
        self.assertIsNone(t.args)

    def test_exception_capture(self):
        """Test that exceptions in threads are captured."""
        class FailingThread(Thread):
            def runIt(self):
                raise ValueError("Test error")

        Thread.isQueueEmpty()  # Clear any existing exceptions

        t = FailingThread("failing")
        t.start()
        t.join()

        # Should not be empty after thread fails
        self.assertFalse(Thread.isQueueEmpty())

    def test_wait_for_exception(self):
        """Test waiting for exceptions from threads."""
        class FailingThread(Thread):
            def runIt(self):
                raise ValueError("Test exception")

        # Clear queue first
        while not Thread.isQueueEmpty():
            try:
                Thread.waitForException(timeout=0.1)
            except Exception:
                pass

        t = FailingThread("failing")
        t.start()

        # Wait for exception
        with self.assertRaises(ValueError) as context:
            Thread.waitForException(timeout=2.0)

        self.assertIn("Test exception", str(context.exception))

    def test_successful_thread(self):
        """Test thread that completes successfully."""
        class SuccessThread(Thread):
            def __init__(self, name):
                super().__init__(name)
                self.completed = False

            def runIt(self):
                time.sleep(0.1)
                self.completed = True

        t = SuccessThread("success")
        t.start()
        t.join()
        self.assertTrue(t.completed)


if __name__ == '__main__':
    unittest.main()
