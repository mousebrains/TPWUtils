#! /usr/bin/env python3
#
# A thread super class that handles exceptions from the actual thread.
# The actual thread run method is called runIt, otherwise it is like a normal
# thread class.
#
# June-2021, Pat Welch, pat@mousebrains.com

from argparse import ArgumentParser, Namespace
from abc import ABC, abstractmethod
import threading
import queue
import logging
import types
#
# Base class for threading which catches exceptions and sends them to a queue
#
class Thread(threading.Thread, ABC):
    '''
    A thread super class that handles exceptions from the actual thread.
    The actual thread run method is called runIt.
    Otherwise the actual thread behaves like a "normal" thread
    '''

    __defaultQueue: queue.Queue[tuple[Exception, types.TracebackType | None]] = queue.Queue()

    def __init__(self, name: str, args: Namespace | None = None,
                 excQueue: queue.Queue | None = None) -> None:
        '''
        name: is the name of the thread saved in self.name and used by logging messages
        args: is saved in self.args
        excQueue: optional exception queue for scoped exception handling;
                  if None, uses the shared class-level default queue
        '''
        super().__init__(daemon=True)
        self.name = name
        self.args = args
        self._excQueue = excQueue if excQueue is not None else Thread.__defaultQueue

    @abstractmethod
    def runIt(self) -> None:
        """Override this method with the thread's main logic."""
        ...

    def run(self) -> None: # Called on thread start
        try:
            self.runIt() # Call the actual class's run function inside a try stanza
        except Exception as e:
            self._excQueue.put((e, e.__traceback__))

    @classmethod
    def isQueueEmpty(cls, excQueue: queue.Queue | None = None) -> bool:
        q = excQueue if excQueue is not None else cls.__defaultQueue
        return q.empty()

    @classmethod
    def waitForException(cls, timeout: float | None = None,
                         excQueue: queue.Queue | None = None) -> None:
        q = excQueue if excQueue is not None else cls.__defaultQueue
        if timeout is None:
            e, tb = q.get()
            raise e.with_traceback(tb)
        while True:
            try:
                e, tb = q.get(timeout=timeout)
                raise e.with_traceback(tb)
            except queue.Empty:
                return

if __name__ == "__main__":
    try:
        from TPWUtils import Logger
    except ImportError:
        import Logger  # type: ignore[no-redef]
    import logging
    import time

    class A(Thread):
        def __init__(self, args: Namespace):
            Thread.__init__(self, "A", args)

        @staticmethod
        def addArgs(parser: ArgumentParser):
            parser.add_argument("--dt", type=float, default=1.7,
                    help="Time to wait to throw an exception")
        def runIt(self) -> None:
            ''' I'll throw an exception after --dt seconds '''
            dt = self.args.dt  # type: ignore[union-attr]
            logging.info("Going to throw an error after %s seconds", dt)
            time.sleep(dt)
            logging.warning("Throwing a NotImplemented exception")
            raise NotImplementedError("Not implemented beyond here.")

    parser = ArgumentParser()
    Logger.addArgs(parser)
    A.addArgs(parser)
    args = parser.parse_args()

    Logger.mkLogger(args)

    thrd = A(args)
    thrd.start()
    try:
        Thread.waitForException()
    except Exception:
        logging.exception("Exception from A")
