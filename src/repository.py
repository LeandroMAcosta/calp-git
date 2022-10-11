import configparser
import os

GITDIR = ".calp"

class Repository:
    
    worktree = "."
    gitdir = GITDIR
    conf = None

    def __init__(self, path: str):
        self.worktree = path
        self.gitdir = os.path.join(path, GITDIR)
        self.conf = configparser.ConfigParser()
        cf = self.build_path("config")
        if os.path.exists(cf):
            self.conf.read([cf])

    def build_path(self, *path):
        return os.path.join(self.gitdir, *path)

    def create_dir(self, *path):
        path = self.build_path(*path)
        if not os.path.exists(path):
            os.makedirs(path)
        return path


def create_repository(path) -> Repository:
    repo = Repository(path)

    if os.path.exists(repo.gitdir):
        raise Exception(f"Git repository already exists at {repo.gitdir}")

    repo.create_dir()
    repo.create_dir("objects")
    repo.create_dir("refs", "heads")
    repo.create_dir("refs", "tags")

    with open(repo.build_path("HEAD"), "w+") as f:
        f.write("ref: refs/heads/master")
    return repo


def repo_find(path=".") -> Repository:
    path = os.path.realpath(path)

    if os.path.isdir(os.path.join(path, GITDIR)):
        return Repository(path)

    parent = os.path.realpath(os.path.join(path, ".."))

    if parent == path:
        # Bottom case
        # os.path.join("/", "..") == "/":
        # If parent == path, then path is root.
        raise Exception("No git directory.")

    # Recursive case
    return repo_find(parent)
