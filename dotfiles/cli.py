#!/usr/bin/env python3
import click

from .common import Skipping, git
from .dotfiles import (
    move_to_dotfiles,
    remove_from_dotfiles,
    setup_dotfiles,
    update_from_repo,
    push_to_repo
)
from . import log


@click.group()
@click.option("--verbose / --noverbose", default=False, help="Be more verbose")
@click.pass_context
def cli(ctx, verbose):
    ctx.ensure_object(dict)

    ctx.obj["VERBOSE"] = verbose


@cli.command()
@click.argument("files", nargs=-1, type=click.Path(exists=True))
def add(files):
    """Add FILES as dotfiles

    This moves the FILES to the dotfiles directory and creates
    a symlink back to the original path.
    """
    for src_path in files:
        try:
            log.message(f"Moving {src_path} to dotfiles ...")
            move_to_dotfiles(src_path)
        except Skipping as e:
            log.warning(f"Skipping {src_path}: {e}")


@click.argument("files", nargs=-1, type=click.Path(exists=True))
@cli.command()
def rm(files):
    """Remove FILES from dotfiles

    Move the FILES from the dotfiles directory to the
    original location, overwriting the symlink.
    """
    for filename in files:
        try:
            log.message(f"Removing {filename} from dotfiles ...")
            remove_from_dotfiles(filename)
        except Skipping as e:
            log.warning(f"Skipping {filename}: {e}")


@cli.command()
def setup():
    """Set up dotfiles in home directory"""
    setup_dotfiles()


@click.argument("dest", nargs=1, type=click.Path(exists=False))
@click.argument("src", nargs=1, type=click.Path(exists=True))
@cli.command()
def mv(src, dest):
    """Rename a dotfile from SRC to DEST."""
    pass


@cli.command()
def sync():
    """Update dotfiles from repo, then push local changes to repo."""
    update_from_repo()
    push_to_repo()


@cli.command()
def update():
    """ Update dotfiles from repository and run setup """
    update_from_repo()


@cli.command()
def push():
    """Push modified dotfiles to repo"""
    push_to_repo()


@cli.command()
def diff():
    """Print differencs between local and pushed dotfiles """
    git("diff")
