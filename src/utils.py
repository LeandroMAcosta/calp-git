from src.repository import GITDIR
from src.colors import color_text

def print_status_messages(status):
    modified = status["modified"]
    untracked = status["untracked"]
    deleted = status["deleted"]

    FAIL = '\033[91m'  # red color
    ENDC = '\033[0m'

    if len(modified):
        print(
            "\nChanges not staged for commit:\n" +
            f"(use '{GITDIR[1:]} add <file>...' to update what will be committed)\n" +
            f"(use '{GITDIR[1:]} restore <file>...' to discard changes in working directory)"
        )
        for file in modified:
            print(color_text("RED","\tmodified: "+file))

    if len(deleted):
        print("\nDeleted files:")
        for file in deleted:
            print(color_text("RED","\t"+file))

    if len(untracked):
        print(
            "\nUntracked files:\n" +
            f"(use '{GITDIR[1:]} add <file>...' to include in what will be committed)"
        )
        for file in untracked:
            print(color_text("RED","\t"+file))

    if len(modified) == 0 and len(deleted) == 0 and len(untracked) == 0:
        print("Nothing to commit (working directory clean)")
