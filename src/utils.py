import os
from src.repository import GITDIR


def get_files_rec(directory):
    files = []
    for path in os.scandir(directory):
        if not path.name.startswith(GITDIR):
            if path.is_file():
                files.append(os.path.join(directory, path))
            else:
                get_files_rec(os.path.join(directory, path))

    return files


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
            print(f"\t{FAIL}modified: {file}{ENDC}")

    if len(deleted):
        print("\nDeleted files:")
        for file in deleted:
            print(f"\t{FAIL}{file}{ENDC}")

    if len(untracked):
        print(
            "\nUntracked files:\n" +
            f"(use '{GITDIR[1:]} add <file>...' to include in what will be committed)"
        )
        for file in untracked:
            print(f"\t{FAIL}{file}{ENDC}")

    if len(modified) == 0 and len(deleted) == 0 and len(untracked) == 0:
        print("Nothing to commit (working directory clean)")
