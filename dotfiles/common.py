import os
import subprocess
from pathlib import Path
from . import log

DOTFILES_DIR = str(Path(os.environ["XDG_DATA_HOME"], "dotfiles"))
DOTFILES_HOME = Path(DOTFILES_DIR).joinpath("home")
DOTFILES_IGNORE = [".git"]

GIT_REMOTE = "origin"
GIT_DEFAULT_BRANCH = "main"


class Skipping(Exception):
    pass


def run(cmdline: [str]) -> None:
    log.verbose(f"Running {cmdline}")
    subprocess.run(cmdline, check=True)


def git(*args) -> None:
    run(["git", "-C", DOTFILES_HOME, *args])
