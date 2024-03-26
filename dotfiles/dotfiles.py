import os
import os.path
from pathlib import Path
from . import log
from .common import git, GIT_REMOTE, GIT_DEFAULT_BRANCH


from .common import DOTFILES_DIR, DOTFILES_HOME, DOTFILES_IGNORE, Skipping


def ls_dotfiles():
    pass


def move_to_dotfiles(src_path):
    src_path = Path(src_path)
    dest_path = DOTFILES_HOME.joinpath(
        src_path.absolute().relative_to(Path.home()))

    if src_path.is_symlink():
        if src_path.resolve() == dest_path:
            raise Skipping("{} already a dotfile, skipping".format(src_path))
        else:
            raise Skipping("{} is a symlink, skipping".format(src_path))
    elif dest_path.exists():
        raise Skipping("{} already exists".format(dest_path))

    parent_dir = dest_path.parent
    parent_dir.mkdir(parents=True, exist_ok=True)

    src_path.rename(dest_path)
    src_path.symlink_to(dest_path)


def remove_from_dotfiles(path):
    dotfiles_path = DOTFILES_HOME.joinpath(
        path.absolute().relative_to(Path.home()))

    if not path.exists():
        raise Skipping(f"{path} does not exist")

    if not path.is_symlink():
        raise Skipping("{path} is not a symlink")

    if path.resolve() != dotfiles_path:
        raise Skipping(f"{path} is not a dotfile")

    if path.is_dir():
        path.rmdir()
    else:
        path.unlink()

    dotfiles_path.rename(path)


def sync_with_repo() -> None:
    push_to_repo()
    update_from_repo()


def update_from_repo() -> None:
    log.message("Pulling dotfiles ...")
    git("fetch")
    git("pull", "--autostash", "--rebase", GIT_REMOTE, GIT_DEFAULT_BRANCH)

    setup_dotfiles()


def push_to_repo() -> None:
    log.message("Pushing dotfiles ...")
    git("add", ".")
    git("commit", "-m", "[dotfiles] automatic commit")
    git("push")


def setup_dotfiles():
    log.message("Creating symlinks to dotfiles ...")
    update_symlinks()
    log.message("Removing broken dotfiles symlinks ...")
    remove_broken_symlinks()
    log.message("Running setup scripts ...")


def remove_broken_symlinks():
    for dirpath, dirnames, filenames in os.walk(home_dir()):
        dirnames = [
            dirname
            for dirname in dirnames
            if (
                os.path.basename(dirname) not in DOTFILES_IGNORE
                and not os.path.samefile(os.path.join(dirpath, dirname),
                                         DOTFILES_DIR)
            )
        ]

        symlinks = [filename for filename in filenames if ()]

        if symlinks:
            print(symlinks)


def update_symlinks():
    for dirpath, dirnames, filenames in os.walk(DOTFILES_HOME):
        dirnames = [
            dirname
            for dirname in dirnames
            if os.path.basename(dirname) not in DOTFILES_IGNORE
        ]
        for dirname in dirnames:
            dest_dirname = make_dest_path(os.path.join(dirpath, dirname))
            make_dir(dest_dirname)

        filenames = [
            filename
            for filename in filenames
            if os.path.basename(filename) not in DOTFILES_IGNORE
        ]
        for filename in filenames:
            src_filename = os.path.join(dirpath, filename)
            src_path, dest_path = make_symlink_paths(src_filename)
            make_symlink(src_path, dest_path)


def make_dir(dirname):
    if os.path.exists(dirname):
        if os.path.isdir(dirname):
            log.verbose(f"skipping mkdir {dirname}, exists")
            return
        else:
            raise Exception(
                f"Trying to make dir {dirname}, "
                "but it already exists and is not a file"
            )

    log.verbose(f"mkdir {dirname}")
    os.mkdir(dirname)


def make_symlink(src_path, dest_path):
    if os.path.exists(dest_path):
        if not os.path.islink(dest_path):
            raise Exception(
                f"Trying to create symlink {dest_path},"
                "but it already exists and is not a symlink"
            )
        elif os.readlink(dest_path) == src_path:
            log.verbose(f"skipping symlink {src_path} → {dest_path}, exists")
            return
        else:
            log.verbose(f"overwriting symlink {dest_path}")
            os.unlink(dest_path)

    log.verbose(f"symlink {src_path} → {dest_path}")
    os.symlink(src_path, dest_path)


def make_dest_path(src_path):
    return os.path.join(home_dir(),
                        os.path.relpath(src_path, start=DOTFILES_HOME))


def make_symlink_paths(src_filename):
    dest_path = make_dest_path(src_filename)
    src_path = os.path.relpath(src_filename, start=os.path.dirname(dest_path))

    return (src_path, dest_path)


def home_dir():
    return os.path.expanduser("~")


def read_link(path):
    dest_path = os.readlink(path)
    abs_dest_path = os.path.join(os.path.dirname(path), dest_path)
    return abs_dest_path
