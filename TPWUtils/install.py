#! /usr/bin/env python3
#
# Install the service(s) and timer(s)
#
# Feb-2022, Pat Welch, pat@mousebrains.com
# June-2023, Pat Welch, pat@mousebrains.com updated for both root and user

from argparse import ArgumentParser, Namespace
from collections.abc import Iterable
from pathlib import Path
import logging
import subprocess
import sys

def makeDirectory(dirname: str, args: Namespace, qUser: bool = False) -> str:
    dir_path = Path(dirname).expanduser().resolve()
    if dir_path.is_dir():
        return str(dir_path)
    cmd = []
    if not qUser and not args.user:
        cmd.append(args.sudo)
    cmd.extend((args.mkdir, "-p", str(dir_path)))
    logging.info("Creating %s", " ".join(cmd))
    if not args.dryrun:
        subprocess.run(cmd, shell=False, check=True)
    return str(dir_path)

def stripComments(fn: str) -> str:
    # NOTE: This is a simple heuristic that strips everything after '#'.
    # It does not handle '#' inside quoted strings in systemd unit files.
    # This is acceptable for file-comparison purposes since both source
    # and target are stripped the same way.
    lines = []
    for line in Path(fn).read_text().splitlines():
        index = line.find("#")
        if index >= 0:
            line = line[:index]
        line = line.strip()
        if line:
            lines.append(line)
    return "\n".join(lines)

def needsToBeCopied(src: str, args: Namespace) -> str | None:
    src_path = Path(src).expanduser().resolve()
    tgt_path = Path(args.serviceDirectory) / src_path.name

    if not args.force and tgt_path.is_file():
        sContent = stripComments(str(src_path))
        tContent = stripComments(str(tgt_path))
        if sContent == tContent:
            return None
    return str(tgt_path)

def copyFiles(items: set, args: Namespace) -> None:
    cmd = []
    if not args.user:
        cmd.append(args.sudo)
    cmd.append(args.cp)
    for item in items:
        a = list(cmd)
        a.extend(item)
        logging.info("Copying %s", " ".join(a))
        if not args.dryrun:
            subprocess.run(a, shell=False, check=True)

def mkSystemctl(args: Namespace, options: tuple[str, ...] | None = None,
                extras: Iterable[str] | None = None, chk: bool = True) -> None:
    cmd = [args.systemctl, "--user"] if args.user else [args.sudo, args.systemctl]
    if options:
        cmd.extend(options)
    if extras:
        cmd.extend(extras)
    logging.info("%s", " ".join(cmd))
    if not args.dryrun:
        subprocess.run(cmd, shell=False, check=chk)

def common(args: Namespace) -> tuple[set | None, set | None, set | None, set | None, set | None]:
    if not args.serviceDirectory:
        args.serviceDirectory = "~/.config/systemd/user" if args.user else "/etc/systemd/system"
    args.serviceDirectory = str(Path(args.serviceDirectory).expanduser().resolve())

    services = set()
    timers = set()
    toEnable = set()
    toStart = set()

    for service in args.service:
        svc_path = Path(service).expanduser().resolve()
        if not svc_path.is_file():
            logging.error("%s does not exist", svc_path)
            return (None, None, None, None, None)
        services.add(str(svc_path))
        timer_path = svc_path.with_suffix(".timer")
        if timer_path.is_file():
            timers.add(str(timer_path))
            toEnable.add(timer_path.name)
            toStart.add(timer_path.name)
        else:
            toEnable.add(svc_path.name)
            toStart.add(svc_path.name)

    allNames = set(Path(f).name for f in services.union(timers))
    return (services, timers, toEnable, toStart, allNames)

def install(args: Namespace) -> int:
    (services, timers, toEnable, toStart, allNames) = common(args)

    if services is None:
        return 1

    if args.logdir:
        args.logdir = makeDirectory(args.logdir, args, True)
    args.serviceDirectory = makeDirectory(args.serviceDirectory, args)

    toCopy = set() # Files that need to be copied
    for fn in services.union(timers):  # type: ignore[union-attr, arg-type]
        tgt = needsToBeCopied(fn, args)
        if tgt:
            toCopy.add((fn, tgt))

    if not toCopy:
        logging.info("Nothing needs to be done")
        return 0

    if toStart:
        mkSystemctl(args, ("stop",), toStart, False)
    if toEnable:
        mkSystemctl(args, ("disable",), toEnable, False)

    copyFiles(toCopy, args)
    mkSystemctl(args, ("daemon-reload",))

    if toEnable:
        mkSystemctl(args, ("enable",), toEnable)

    if toStart:
        mkSystemctl(args, ("start",), toStart)

    if args.user:
        cmd = (args.loginctl, "enable-linger")
        logging.info("Enable Linger %s", " ".join(cmd))
        if not args.dryrun:
            subprocess.run(cmd, shell=False, check=True)

    mkSystemctl(args, ("--no-pager", "status"), allNames, False)

    if timers:
        mkSystemctl(args, ("--no-pager", "list-timers"), (Path(t).name for t in timers), False)

    return 0

def uninstall(args: Namespace) -> int:
    (services, timers, toEnable, toStart, allNames) = common(args)

    if allNames is None:
        return 1

    toDelete = set()
    for fn in allNames:
        ofn = Path(args.serviceDirectory) / fn
        if ofn.is_file():
            toDelete.add(str(ofn))

    if not toDelete:
        return 0
    if toStart:
        mkSystemctl(args, ("stop",), toStart, False)
    if toEnable:
        mkSystemctl(args, ("disable",), toEnable, False)

    cmd = [args.rm, "-f"] if args.user else [args.sudo, args.rm, "-f"]
    cmd.extend(toDelete)
    logging.info("Removing %s", " ".join(cmd))
    if not args.dryrun:
        subprocess.run(cmd, shell=False, check=True)

    mkSystemctl(args, ("daemon-reload",))
    return 0

def addArgs(parser: ArgumentParser) -> None:
    action_grp = parser.add_mutually_exclusive_group()
    action_grp.add_argument("--install", action="store_true", help="Install services and timers")
    action_grp.add_argument("--uninstall", action="store_true", help="remove services and timers")

    mode_grp = parser.add_mutually_exclusive_group()
    mode_grp.add_argument("--user", action="store_true", help="Install in user space")
    mode_grp.add_argument("--system", action="store_true", help="Install in system space")

    cmd_grp = parser.add_argument_group("Command paths")
    cmd_grp.add_argument("--sudo", type=str, default="sudo", help="sudo executable")
    cmd_grp.add_argument("--systemctl", type=str, default="systemctl",
                     help="systemctl executable")
    cmd_grp.add_argument("--loginctl", type=str, default="loginctl",
                     help="loginctl executable")
    cmd_grp.add_argument("--mkdir", type=str, default="mkdir", help="mkdir executable")
    cmd_grp.add_argument("--cp", type=str, default="cp", help="cp executable")
    cmd_grp.add_argument("--rm", type=str, default="rm", help="rm executable")

    svc_grp = parser.add_argument_group("Service/timer related options")
    svc_grp.add_argument("--force", action="store_true", help="Force reloading ...")
    svc_grp.add_argument("--serviceDirectory", type=str, help="Where to copy service file to")
    svc_grp.add_argument("--service", type=str, required=True, action="append", help="Service file(s)")
    svc_grp.add_argument("--logdir", type=str, default="~/logs", help="Where logfiles are stored")
    svc_grp.add_argument("--dryrun", action="store_true", help="Do not actually install anything")

if __name__ == "__main__":
    try:
        from TPWUtils import Logger
    except ImportError:
        import Logger  # type: ignore[no-redef]

    parser = ArgumentParser()
    Logger.addArgs(parser)
    addArgs(parser)
    args = parser.parse_args()

    Logger.mkLogger(args, fmt="%(asctime)s %(levelname)s: %(message)s", qThreaded=False)

    sys.exit(uninstall(args) if args.uninstall else install(args))
