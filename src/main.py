import sys

from src.cli import commands


def main(argv=sys.argv[1:]):
    if len(argv) < 1:
        print(f"Usage: calp <{'|'.join(commands.keys())}> [OPTIONS...]")
        return

    cmd = argv[0]
    try:
        cmd_cls = commands[cmd]
    except KeyError:
        print(f"No such subcommand: {cmd}")
        return
    return cmd_cls().run(argv)
