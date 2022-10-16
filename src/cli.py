import argparse
import optparse

from src import plumbing, porcelain
from src.repository import repo_find


class Command:
    def run(self, args):
        raise NotImplementedError


class CmdInit(Command):
    def run(self, args):
        parser = optparse.OptionParser()
        parser.add_option(
            '--path',
            dest="path",
            default='.',
            help="Where to create the repository."
        )
        options, args = parser.parse_args(args)
        porcelain.init(options.path)


class CmdAdd(Command):
    def run(self, args):
        ...


class CmdLog(Command):
    def run(self, args):
        repo = repo_find()
        print(repo.worktree)
        print(repo.gitdir)


class CmdCommit(Command):
    def run(self, args):
        ...


class CmdHashObject(Command):
    def run(self, args):
        parser = optparse.OptionParser()
        parser.add_option(
            "-t",
            dest="type",
            default="blob",
            choices=["blob", "commit", "tree"],
            help="Specify the type."
        )
        parser.add_option(
            "-w",
            dest="write",
            action="store_true",
            help="Actually write the object into the object database."
        )
        parser.add_option(
            "--path",
            dest="path",
            help="Hash object as it were located at the given path."
        )
        options, args = parser.parse_args(args)
        plumbing.hash_object(options.type, options.path, options.write)


class CmdCatFile(Command):
    def run(self, args):
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "type",
            choices=["blob", "commit", "tag", "tree"],
            help="Specify the type"
        )
        parser.add_argument(
            "object",
            help="The object to display"
        )
        args = parser.parse_args(args)
        plumbing.cat_file(args.type, args.object)


commands = {
    'init': CmdInit,
    'add': CmdAdd,
    'log': CmdLog,
    'commit': CmdCommit,
    'hash-object': CmdHashObject,
    'cat-file': CmdCatFile,
}
