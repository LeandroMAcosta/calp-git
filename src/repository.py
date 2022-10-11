import configparser
import os


class Repository:
    
    worktree = "."
    gitdir = ".calp"
    conf = None

    def __init__(self, path: str):
        self.worktree = path
        self.gitdir = os.path.join(path, ".calp")
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


def create_repository(path):
    repo = Repository(path)
    repo.create_dir()
    repo.create_dir("objects")
    repo.create_dir("refs", "heads")
    repo.create_dir("refs", "tags")

    with open(repo.build_path("HEAD"), "w+") as f:
        f.write("ref: refs/heads/master")
    return repo
