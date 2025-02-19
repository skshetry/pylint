# Licensed under the GPL: https://www.gnu.org/licenses/old-licenses/gpl-2.0.html
# For details: https://github.com/PyCQA/pylint/blob/main/LICENSE
# Copyright (c) https://github.com/PyCQA/pylint/blob/main/CONTRIBUTORS.txt

import configparser
import os
import sys
import warnings
from pathlib import Path
from typing import Iterator, Optional, Union

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


def _toml_has_config(path: Union[Path, str]) -> bool:
    with open(path, mode="rb") as toml_handle:
        try:
            content = tomllib.load(toml_handle)
        except tomllib.TOMLDecodeError as error:
            print(f"Failed to load '{path}': {error}")
            return False
    return "pylint" in content.get("tool", [])


def _cfg_has_config(path: Union[Path, str]) -> bool:
    parser = configparser.ConfigParser()
    try:
        parser.read(path, encoding="utf-8")
    except configparser.Error:
        return False
    return any(section.startswith("pylint.") for section in parser.sections())


def find_default_config_files() -> Iterator[str]:
    """Find all possible config files."""
    rc_names = ("pylintrc", ".pylintrc")
    config_names = rc_names + ("pyproject.toml", "setup.cfg")
    for config_name in config_names:
        if os.path.isfile(config_name):
            if config_name.endswith(".toml") and not _toml_has_config(config_name):
                continue
            if config_name.endswith(".cfg") and not _cfg_has_config(config_name):
                continue

            yield os.path.abspath(config_name)

    if os.path.isfile("__init__.py"):
        curdir = os.path.abspath(os.getcwd())
        while os.path.isfile(os.path.join(curdir, "__init__.py")):
            curdir = os.path.abspath(os.path.join(curdir, ".."))
            for rc_name in rc_names:
                rc_path = os.path.join(curdir, rc_name)
                if os.path.isfile(rc_path):
                    yield rc_path

    if "PYLINTRC" in os.environ and os.path.exists(os.environ["PYLINTRC"]):
        if os.path.isfile(os.environ["PYLINTRC"]):
            yield os.environ["PYLINTRC"]
    else:
        user_home = os.path.expanduser("~")
        if user_home not in ("~", "/root"):
            home_rc = os.path.join(user_home, ".pylintrc")
            if os.path.isfile(home_rc):
                yield home_rc
            home_rc = os.path.join(user_home, ".config", "pylintrc")
            if os.path.isfile(home_rc):
                yield home_rc

    if os.path.isfile("/etc/pylintrc"):
        yield "/etc/pylintrc"


def find_pylintrc() -> Optional[str]:
    """Search the pylint rc file and return its path if it finds it, else return None."""
    # pylint: disable-next=fixme
    # TODO: Remove this function in 3.0
    warnings.warn(
        "find_pylintrc and the PYLINTRC constant have been deprecated. "
        "Use find_default_config_files if you want access to pylint's configuration file "
        "finding logic.",
        DeprecationWarning,
    )
    for config_file in find_default_config_files():
        if config_file.endswith("pylintrc"):
            return config_file
    return None
