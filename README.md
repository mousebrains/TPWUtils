# This is a collection of my Python 3 utilities

- `Logger.py` set up a logger which supports console, rolling file, and/or SMTP logging methods
  - `addArgs(parser:argparse.ArgumentParser)` adds command line arguments for setting up logging
  - `mkLogger(args:argparse.ArgumentParser, fmt:str, name:str)` uses the args to setup the logger
    - *fmt* is the logging message format, by default "%(asctime)s %(threadName)s %(levelname)s: %(message)s"
    - *name* is the logger to setup

- `Thread.py` is a *threading.Thread* class which catches exceptions and sends them to a queue. Then the main thread can wait on the queue for a problem to arise in any of the threads.

- `INotify.py` is a thread which waits for modifications in a file system then forwards the modifications to a set of queues for other threads to process. It handles adding/removing of directories.

- `GreatCircle.py` calculates great circle distances on the earth in meters using Vincenty's method. Compared against Matlab's distance function, distance.sample.nc, it should give a maximum difference around 1e-7.

- `Credentials.py` loads credentials from YAML files with automatic prompting if the file doesn't exist
  - `getCredentials(fn:str)` returns a tuple of (username, password) from the specified YAML file

- `SingleInstance.py` ensures only one instance of a program runs at a time using Unix abstract sockets
  - Use as a context manager: `with SingleInstance(key) as single:`

- `loadAndExecuteSQL.py` loads and executes SQL commands from a file with optional table existence checking
  - `loadAndExecuteSQL(db, fn:str, tableName:str=None)` executes SQL from a file, skipping if table already exists

- `install.py` installs and manages systemd services and timers for both user and system contexts
  - `addArgs(parser:ArgumentParser)` adds command line arguments for service installation
  - `install(args:ArgumentParser)` installs services and timers
  - `uninstall(args:ArgumentParser)` removes services and timers

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.
