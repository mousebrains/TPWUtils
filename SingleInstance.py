#! /usr/bin/env python3
#
# Using socket listener to check there is only one listener for a specified port
#
# June-2022, Pat Welch, pat@mousebrains.com

import socket
import logging
import os
import sys
import platform
import tempfile

class SingleInstance: # Must be used with with statement
    def __init__(self, key: str | None = None) -> None:
        self.__key = os.path.abspath(os.path.expanduser(sys.argv[0])) if key is None else key
        self.__socket_path = None

    def __enter__(self) -> "SingleInstance":
        try:
            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

            # Linux supports abstract sockets (prefixed with \0)
            # macOS requires a real file path
            if platform.system() == "Linux":
                socket_name = '\0' + self.__key  # Abstract socket
            else:
                # Create a socket file in temp directory for macOS/other systems
                self.__socket_path = os.path.join(
                    tempfile.gettempdir(),
                    f".singleinstance_{os.path.basename(self.__key)}"
                )
                # Check if socket is already in use by trying to connect
                if os.path.exists(self.__socket_path):
                    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as test_sock:
                        try:
                            test_sock.connect(self.__socket_path)
                            # If connect succeeds, another instance is running
                            raise OSError("Socket already in use")
                        except (ConnectionRefusedError, FileNotFoundError):
                            # Socket file exists but not in use (stale), remove it
                            try:
                                os.unlink(self.__socket_path)
                            except OSError:
                                pass
                socket_name = self.__socket_path

            s.bind(socket_name)
            s.listen(1)  # Start listening to make socket "in use"
            self.__socket = s
            return self
        except Exception:
            logging.exception("Unable to connect to %s", self.__key)
            self.__socket = None
            raise RuntimeError(f"Another instance is already running with key: {self.__key}")

    def __exit__(self, excType, excValue, excTraceback) -> None:
        if self.__socket is not None:
            self.__socket.close()
        self.__socket = None
        # Clean up socket file on macOS
        if self.__socket_path and os.path.exists(self.__socket_path):
            try:
                os.unlink(self.__socket_path)
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
