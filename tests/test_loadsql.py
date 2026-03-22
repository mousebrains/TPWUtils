"""Unit tests for loadAndExecuteSQL module."""

import unittest
import os
import tempfile
from unittest.mock import MagicMock
from TPWUtils.loadAndExecuteSQL import loadAndExecuteSQL


class TestLoadAndExecuteSQL(unittest.TestCase):
    """Test the loadAndExecuteSQL function."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _make_sql_file(self, content):
        path = os.path.join(self.test_dir, "test.sql")
        with open(path, "w") as f:
            f.write(content)
        return path

    def test_table_already_exists(self):
        """Should return True without executing SQL if table exists."""
        db = MagicMock()
        cursor = MagicMock()
        db.cursor.return_value = cursor
        cursor.__iter__ = MagicMock(return_value=iter([(1,)]))

        result = loadAndExecuteSQL(db, "dummy.sql", tableName="existing_table")
        self.assertTrue(result)
        db.commit.assert_not_called()

    def test_executes_sql_no_table_check(self):
        """Should execute SQL from file when no tableName given."""
        sql = "CREATE TABLE test (id INT);"
        path = self._make_sql_file(sql)

        db = MagicMock()
        cursor = MagicMock()
        db.cursor.return_value = cursor

        result = loadAndExecuteSQL(db, path)
        self.assertTrue(result)
        cursor.execute.assert_called_with(sql)
        db.commit.assert_called_once()

    def test_executes_sql_when_table_not_found(self):
        """Should execute SQL when table doesn't exist."""
        sql = "CREATE TABLE test (id INT);"
        path = self._make_sql_file(sql)

        db = MagicMock()
        cursor = MagicMock()
        db.cursor.return_value = cursor
        cursor.__iter__ = MagicMock(return_value=iter([(0,)]))

        result = loadAndExecuteSQL(db, path, tableName="test")
        self.assertTrue(result)
        db.commit.assert_called_once()

    def test_handles_sql_execution_error(self):
        """Should return False and rollback when cursor.execute raises."""
        sql = "INVALID SQL;"
        path = self._make_sql_file(sql)

        db = MagicMock()
        cursor = MagicMock()
        cursor.close = MagicMock()
        db.cursor.return_value = cursor
        cursor.execute.side_effect = Exception("SQL error")

        result = loadAndExecuteSQL(db, path)
        self.assertFalse(result)
        db.rollback.assert_called_once()

    def test_rollback_failure_handled(self):
        """Should handle rollback failure gracefully."""
        path = self._make_sql_file("SELECT 1;")

        db = MagicMock()
        cursor = MagicMock()
        cursor.close = MagicMock()
        db.cursor.return_value = cursor
        cursor.execute.side_effect = Exception("SQL error")
        db.rollback.side_effect = Exception("Connection lost")

        result = loadAndExecuteSQL(db, path)
        self.assertFalse(result)

    def test_handles_missing_file(self):
        """Should return False if SQL file doesn't exist."""
        db = MagicMock()
        cursor = MagicMock()
        db.cursor.return_value = cursor

        result = loadAndExecuteSQL(db, "/nonexistent/file.sql")
        self.assertFalse(result)
        db.rollback.assert_called_once()


if __name__ == "__main__":
    unittest.main()
