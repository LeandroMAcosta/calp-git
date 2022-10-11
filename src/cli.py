import optparse
from src.repository import repo_find

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
        repo = repo_find()     
        print(repo.worktree)
        print(repo.gitdir)

class CmdCommit(Command):
    def run(self, args):
        ...


commands = {
    'init': CmdInit,
    'add': CmdAdd,
    'log': CmdLog,
    'commit': CmdCommit,
}
