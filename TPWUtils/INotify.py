#! /usr/bin/env python3
#
# Use watchdog to handle file system notification and send
# the notification to a queue
#
# Originally used pyinotify (Linux-only, unmaintained since 2015).
# Migrated to watchdog for cross-platform support.
#

from argparse import ArgumentParser, Namespace
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
import queue
import logging
import time
try:
    from .Thread import Thread # As a module
except ImportError:
    from Thread import Thread  # type: ignore[no-redef]


class _QueueHandler(FileSystemEventHandler):
    """Push file system events onto a queue as (timestamp, path) tuples."""

    def __init__(self, q: queue.Queue[tuple[float, str]]) -> None:
        super().__init__()
        self.__queue = q

    def on_any_event(self, event: FileSystemEvent) -> None:
        t0 = time.time()
        fn = str(event.src_path)
        self.__queue.put((t0, fn))
        logging.debug("Event %s, %s", fn, event.event_type)


class INotify(Thread):
    """Use watchdog to monitor file system updates."""

    def __init__(self, args: Namespace, flags: int | None = None) -> None:
        super().__init__("INotify", args)
        self.__observer = Observer()
        self.queue: queue.Queue[tuple[float, str]] = queue.Queue()
        self.__handler = _QueueHandler(self.queue)

    def addTree(self, tgt: str) -> None:
        self.addWatch(tgt, qRecursive=True)

    def addWatch(self, tgt: str, mask: int | None = None,
                 qRecursive: bool = False, qAutoAdd: bool = False) -> bool:
        path = Path(tgt).expanduser().resolve()
        if path.is_dir():
            self.__observer.schedule(self.__handler, str(path), recursive=qRecursive)
            logging.info("Added watch for %s, recursive=%s", path, qRecursive)
            return True
        logging.error("Path %s does not exist", path)
        return False

    def runIt(self) -> None:
        logging.info("Starting observer")
        self.__observer.start()
        try:
            while self.__observer.is_alive():
                self.__observer.join(1)
        finally:
            self.__observer.stop()
            self.__observer.join()
        logging.warning("Observer stopped")

if __name__ == "__main__":
    try:
        from TPWUtils import Logger
    except ImportError:
        import Logger  # type: ignore[no-redef]

    class Reader(Thread):
        def __init__(self, args: Namespace, q: queue.Queue) -> None:
            super().__init__("Reader", args)
            self.__queue = q

        def runIt(self) -> None:
            q = self.__queue
            while True:
                (t0, fn) = q.get()
                q.task_done()
                logging.info("%s %s", t0, fn)

    parser = ArgumentParser()
    Logger.addArgs(parser)
    parser.add_argument("tgt", nargs="+", help="Directories to watch")
    args = parser.parse_args()

    Logger.mkLogger(args)

    i = INotify(args)
    rdr = Reader(args, i.queue)
    i.start()
    rdr.start()
    for tgt in args.tgt:
        i.addTree(tgt)

    try:
        Thread.waitForException()
    except Exception:
        logging.exception("Exception from INotify")
