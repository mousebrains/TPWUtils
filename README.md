# This is a collection of my Python 3 utilities

- `Logger.py` creates a logger which supports console, rolling file, and/or SMTP logging methods 
  - `addArgs(parser:argparse.ArgumentParser)` adds command line arguments for setting up logging
  - `mkLogger(args:argparse.ArgumentParser, fmt:str, name:str)` uses the args to setup the logger

- `Thread.py` is a *threading.Thread* class which catches exceptions and sends them to a queue. Then the main thread can wait on the queue for a problem to arise in any of the threads.

