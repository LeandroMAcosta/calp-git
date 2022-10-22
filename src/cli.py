import argparse
import optparse

from src.repository import find_repository
from src.utils import print_status_messages

from . import plumbing, porcelain


class Command:
    def run(self, args):
        raise NotImplementedError


class CmdInit(Command):
    def run(self, args):
        parser = optparse.OptionParser()
        parser.add_option(
            "--path", dest="path", default=".", help="Where to create the repository."
        )
        options, args = parser.parse_args(args)
        porcelain.init(options.path)


class CmdStatus(Command):
    def run(self, args):
        STATUS = porcelain.status()
        print_status_messages(STATUS)

class CmdCheckout(Command):
    def run(self, args):
        parser = optparse.OptionParser()
        parser.add_option(
            "-b",
            dest="new_branch",
            action="store_true",
            help="Name of the branch.",
        )
        options, args = parser.parse_args(args)
        porcelain.checkout(options.new_branch, args)

class CmdAdd(Command):
    def run(self, args):
        parser = argparse.ArgumentParser()
        parser.add_argument("paths", nargs="+")
        args = parser.parse_args(args)
        porcelain.add(args.paths)


class CmdLog(Command):
    def run(self, args):
        repo = find_repository()
        print(repo.worktree)
        print(repo.gitdir)
        # TODO: Implement


class CmdCommit(Command):
    def run(self, args):
        # required -m message
        parser = argparse.ArgumentParser()
        parser.add_argument("-m", "--message", required=True)
        args = parser.parse_args(args)
        porcelain.commit(args.message)


class CmdLsTree(Command):
    def run(self, args):
        parser = optparse.OptionParser()
        parser.add_option("--tree-ish", dest="tree_ish", help="Tree-ish of the tree.")
        options, args = parser.parse_args(args)
        if options.tree_ish is None:
            parser.error("tree-ish is required")

        items = plumbing.ls_tree(options.tree_ish)
        for mode, type, sha, path in items:
            print(f"{mode} {type} {sha}\t{path}")


class CmdHashObject(Command):
    def run(self, args):
        parser = optparse.OptionParser()
        parser.add_option(
            "-t",
            dest="type",
            default="blob",
            choices=["blob", "commit", "tree"],
            help="Specify the type.",
        )
        parser.add_option(
            "-w",
            dest="write",
            action="store_true",
            help="Actually write the object into the object database.",
        )
        parser.add_option(
            "--path",
            dest="path",
            help="Hash object as it were located at the given path.",
        )
        options, args = parser.parse_args(args)
        if options.type == "blob":
            sha = plumbing.hash_object(
                options.type, path=options.path, write=options.write
            )
        else:
            sha = plumbing.hash_object(
                options.type, data=options.path, write=options.write
            )
        print(sha)


class CmdCatFile(Command):
    def run(self, args):
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "type", choices=["blob", "commit", "tag", "tree"], help="Specify the type"
        )
        parser.add_argument("object", help="The object to display")
        args = parser.parse_args(args)
        plumbing.cat_file(args.type, args.object)


commands = {
    "checkout": CmdCheckout,
    "init": CmdInit,
    "status": CmdStatus,
    "add": CmdAdd,
    "log": CmdLog,
    "commit": CmdCommit,
    "hash-object": CmdHashObject,
    "cat-file": CmdCatFile,
    "ls-tree": CmdLsTree,
}
