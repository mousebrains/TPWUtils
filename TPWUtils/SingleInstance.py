#! /usr/bin/env python3
#
# Using socket listener to check there is only one listener for a specified port
#
# June-2022, Pat Welch, pat@mousebrains.com

import socket
import logging
from pathlib import Path
import sys
import platform
import tempfile

class SingleInstance: # Must be used with with statement
    def __init__(self, key: str | None = None) -> None:
        self.__key: str = str(Path(sys.argv[0]).resolve()) if key is None else key
        self.__socket_path: str | None = None
        self.__socket: socket.socket | None = None

    def __enter__(self) -> "SingleInstance":
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            if platform.system() == "Linux":
                socket_name = '\0' + self.__key  # Abstract socket
            else:
                self.__socket_path = str(
                    Path(tempfile.gettempdir()) / f".singleinstance_{Path(self.__key).name}"
                )
                socket_name = self.__socket_path

            try:
                s.bind(socket_name)
            except OSError:
                if self.__socket_path is None:
                    raise  # Linux abstract sockets can't be stale
                # macOS/other: check if existing socket is active or stale
                with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as test_sock:
                    try:
                        test_sock.connect(socket_name)
                        raise OSError(f"Socket {socket_name} is actively in use")
                    except ConnectionRefusedError:
                        Path(socket_name).unlink()
                        s.bind(socket_name)

            s.listen(1)
            self.__socket = s
            return self
        except Exception as e:
            s.close()
            logging.exception("Unable to bind to %s", self.__key)
            self.__socket = None
            raise RuntimeError(
                f"Another instance is already running with key: {self.__key}"
            ) from e

    def __exit__(self, excType, excValue, excTraceback) -> None:
        if self.__socket is not None:
            self.__socket.close()
        self.__socket = None
        # Clean up socket file on macOS
        if self.__socket_path:
            sock_path = Path(self.__socket_path)
            if sock_path.exists():
                try:
                    sock_path.unlink()
                except OSError:
                    pass

if __name__ == "__main__":
    from argparse import ArgumentParser
    import time

    parser = ArgumentParser()
    parser.add_argument("--uniqueName", type=str,
            help="Single instance unique keyword for locking a process")
    parser.add_argument("--dt", type=float, default=100, help="Time to sleep")
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s: %(message)s")
   
    try:
        with SingleInstance(args.uniqueName):
            logging.info("Sleeping for %s seconds", args.dt)
            time.sleep(args.dt)
            logging.info("Done sleeping")
    except Exception:
        logging.exception("Unexpected exception")
