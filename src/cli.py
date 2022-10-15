import optparse
from src.repository import find_repository

from src import porcelain


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
        repo = find_repository()     
        print(repo.worktree)
        print(repo.gitdir)
        # TODO: Implement


class CmdCommit(Command):
    def run(self, args):
        ...


class CmdLsTree(Command):
    def run(self, args):
        parser = optparse.OptionParser()
        parser.add_option(
            '--tree-ish',
            dest="tree_ish",
            help="Tree-ish of the tree."
        )
        options, args = parser.parse_args(args)
        porcelain.ls_tree(options.tree_ish)


commands = {
    'init': CmdInit,
    'add': CmdAdd,
    'log': CmdLog,
    'commit': CmdCommit,
    'ls-tree': CmdLsTree,
}
