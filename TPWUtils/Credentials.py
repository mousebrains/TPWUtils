#
# load credentials
#
import os
from pathlib import Path
import logging
import yaml
import getpass

def getCredentials(fn: str) -> tuple[str, str]:
    fn_path = Path(fn).expanduser().resolve()
    if fn_path.is_file():
        try:
            info = yaml.safe_load(fn_path.read_text())
            if info is not None and "username" in info and "password" in info:
                return (info["username"], info["password"])
            logging.error("%s is not properly formatted or is empty", fn_path)
        except Exception as e:
            logging.warning("Unable to open %s, %s", fn_path, str(e))

    logging.info("Going to build a fresh credentials file, %s", fn_path)
    info = {
            "username": input("Enter username: "),
            "password": getpass.getpass("Enter password: "),
            }

    if not fn_path.parent.is_dir():
        logging.info("Creating %s", fn_path.parent)
        fn_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)

    fd = os.open(str(fn_path), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as fp:
        yaml.dump(info, fp, indent=4, sort_keys=True)
    return (info["username"], info["password"])
