# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TPWUtils is a collection of reusable Python 3 utilities for common development tasks including logging, threading, file system monitoring, geographic calculations, credential management, and system service installation. Each module is standalone and can be used independently.

## Testing

Run all tests:
```bash
python3 -m unittest discover -p "test_*.py" -v
```

Run specific test file:
```bash
python3 -m unittest test_thread.py -v
python3 -m unittest test_greatcircle.py -v
python3 -m unittest test_logger.py -v
```

Run specific test:
```bash
python3 -m unittest test_thread.TestThread.test_exception_capture -v
```

## Code Architecture

### Thread Exception Handling Pattern

The `Thread.py` module implements a thread exception propagation pattern using a static queue:

- Threads inherit from `Thread` and implement `runIt()` instead of `run()`
- Exceptions raised in any thread are captured and pushed to `Thread.__queue`
- Main thread calls `Thread.waitForException(timeout)` to wait for any thread failure
- The exception is re-raised in the main thread, preserving the original exception type

All threads using this pattern should be created as daemon threads.

### Logger Configuration

The `Logger.py` module uses a builder pattern:

1. Call `Logger.addArgs(parser)` to add logging arguments to ArgumentParser
2. Parse arguments to get a Namespace object
3. Call `Logger.mkLogger(args, fmt=None, name=None, qThreaded=False)` to configure logging
   - `qThreaded=True` includes thread names in log format
   - Returns a configured logger instance

### Platform-Specific Socket Handling

`SingleInstance.py` uses Unix domain sockets with platform detection:

- **Linux**: Abstract sockets (prefixed with `\0`) that exist only in memory
- **macOS/Other**: File-based sockets in temp directory with stale socket detection
- Always use as a context manager to ensure proper cleanup

### GreatCircle Numerical Stability

`GreatCircle.py` implements Vincenty's inverse formula with edge case handling:

- Identical points return zero immediately before entering iterative loop
- Antipodal/near-antipodal points use epsilon protection (1e-12) to prevent division by zero
- Uses `np.errstate` to suppress expected warnings during convergence
- Filters NaN/Inf from final results, replacing with zero
- All functions accept scalar or numpy array inputs

### Database Portability

`loadAndExecuteSQL.py` uses INFORMATION_SCHEMA for database portability:

```python
cur.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_name=%s;", (tableName,))
```

This works across PostgreSQL, MySQL, and other SQL databases, not just PostgreSQL-specific catalogs.

## Type Hints

This codebase uses Python 3.10+ type hint syntax:

- Use `type1 | type2` instead of `Union[type1, type2]`
- Use `type | None` instead of `Optional[type]`
- Use `np.ndarray` not `np.array` for numpy array type hints
- ArgumentParser is only for the parser object; use `Namespace` for parsed args

## Module Entry Points

Each module can be run standalone for testing:

```bash
python3 Thread.py --dt 2.0        # Test exception handling after 2 seconds
python3 Logger.py --debug         # Test logging configuration
python3 GreatCircle.py            # Run distance calculation examples
python3 SingleInstance.py --uniqueName test --dt 5  # Test single instance locking
```
