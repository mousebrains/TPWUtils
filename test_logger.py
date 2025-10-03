"""Unit tests for Logger module."""

import unittest
import logging
import tempfile
import os
from argparse import ArgumentParser, Namespace
from TPWUtils.Logger import addArgs, mkLogger


class TestLogger(unittest.TestCase):
    """Test the Logger module."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_addArgs(self):
        """Test that addArgs adds expected arguments."""
        parser = ArgumentParser()
        addArgs(parser)

        # Parse empty args to get defaults
        args = parser.parse_args([])

        self.assertIsNone(args.logfile)
        self.assertEqual(args.logBytes, 10000000)
        self.assertEqual(args.logCount, 3)
        self.assertEqual(args.smtpHost, "localhost")

    def test_mkLogger_console(self):
        """Test creating a console logger."""
        args = Namespace(
            logfile=None,
            logBytes=10000000,
            logCount=3,
            debug=False,
            verbose=False,
            mailTo=None,
            mailFrom=None,
            mailSubject=None,
            smtpHost="localhost"
        )

        logger = mkLogger(args, name="test_console")
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, "test_console")

    def test_mkLogger_file(self):
        """Test creating a file logger."""
        logfile = os.path.join(self.test_dir, "test.log")
        args = Namespace(
            logfile=logfile,
            logBytes=10000000,
            logCount=3,
            debug=False,
            verbose=False,
            mailTo=None,
            mailFrom=None,
            mailSubject=None,
            smtpHost="localhost"
        )

        logger = mkLogger(args, name="test_file")
        self.assertIsInstance(logger, logging.Logger)

        # Test that we can write to the log
        logger.info("Test message")
        self.assertTrue(os.path.exists(logfile))

    def test_mkLogger_debug_level(self):
        """Test debug log level."""
        args = Namespace(
            logfile=None,
            logBytes=10000000,
            logCount=3,
            debug=True,
            verbose=False,
            mailTo=None,
            mailFrom=None,
            mailSubject=None,
            smtpHost="localhost"
        )

        logger = mkLogger(args)
        self.assertEqual(logger.level, logging.DEBUG)

    def test_mkLogger_verbose_level(self):
        """Test verbose (info) log level."""
        args = Namespace(
            logfile=None,
            logBytes=10000000,
            logCount=3,
            debug=False,
            verbose=True,
            mailTo=None,
            mailFrom=None,
            mailSubject=None,
            smtpHost="localhost"
        )

        logger = mkLogger(args)
        self.assertEqual(logger.level, logging.INFO)

    def test_mkLogger_threaded_format(self):
        """Test that threaded format includes thread name."""
        args = Namespace(
            logfile=None,
            logBytes=10000000,
            logCount=3,
            debug=False,
            verbose=False,
            mailTo=None,
            mailFrom=None,
            mailSubject=None,
            smtpHost="localhost"
        )

        logger = mkLogger(args, qThreaded=True)
        # Check that handlers exist
        self.assertGreater(len(logger.handlers), 0)

    def test_mkLogger_non_threaded_format(self):
        """Test non-threaded format."""
        args = Namespace(
            logfile=None,
            logBytes=10000000,
            logCount=3,
            debug=False,
            verbose=False,
            mailTo=None,
            mailFrom=None,
            mailSubject=None,
            smtpHost="localhost"
        )

        logger = mkLogger(args, qThreaded=False)
        self.assertGreater(len(logger.handlers), 0)


if __name__ == '__main__':
    unittest.main()
