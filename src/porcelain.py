import os
from typing import List

from src import plumbing
from src.algorithms import (ancestors_until_lca, get_ancestors, get_files_rec,
                            read_object)
from src.colors import color_text
from src.index import IndexEntry, read_entries
from src.objects.base import is_sha1
from src.objects.commit import Commit
from src.repository import GITDIR, create_repository, find_repository
from src.utils import print_status_messages


def init(path):
    """
    Create an empty Calp repository.

    https://git-scm.com/docs/git-init
    """
    create_repository(path)


def add(paths: List[str]):
    """
    Add file contents to the index.

    This command updates the index using the current content found in the working tree,
    to prepare the content staged for the next commit. It typically adds the current content
    of existing paths as a whole, but with some options it can also be used to add content
    with only part of the changes made to the working tree files applied, or remove paths that
     do not exist in the working tree anymore.

    The "index" holds a snapshot of the content of the working tree, and it is this snapshot
    that is taken as the contents of the next commit. Thus after making any changes to the
    working tree, and before running the commit command, you must use the add command to add
    any new or modified files to the index.

    This command can be performed multiple times before a commit. It only adds the content
    of the specified file(s) at the time the add command is run; if you want subsequent
    changes included in the next commit, then you must run git add again to add the new
    content to the index.

    https://git-scm.com/docs/git-add
    """
    # paths: ["A/1.txt", "2.txt"]
    # Read the entries from the staging area in the index file
    entries: List[IndexEntry] = read_entries()
    entries = [entry for entry in entries if entry.path not in paths]

    for path in paths:
        if path.startswith(GITDIR) or path in [".", ".."]:
            raise Exception(f"Cannot add {path} to the index")

    for path in paths:
        # TODO: Handle directories
        if os.path.exists(path):
            hash = plumbing.hash_object("blob", path=path, write=True)
            entry = IndexEntry(path, hash)
            entries.append(entry)

    plumbing.update_index(entries)


def commit(message):
    """
    Record changes to the repository.

    Create a new commit containing the current contents of the index and the given log
    message describing the changes. The new commit is a direct child of HEAD.

    https://git-scm.com/docs/git-commit
    """
    tree_sha1 = plumbing.write_tree()
    commit_sha1 = plumbing.commit_tree(tree_sha1, message)
    current_branch = plumbing.get_current_branch()
    plumbing.update_ref(current_branch, commit_sha1)
    return commit_sha1


def status():
    """
    Show the working tree status.
    Displays paths that have differences between the index file and the current HEAD commit,
    paths that have differences between the working tree and the index file, and paths in
    the working tree that are not tracked by Calp (our Git implementation).

    https://git-scm.com/docs/git-status
    """
    entries: List[IndexEntry] = read_entries()
    repo = find_repository()
    files = get_files_rec(repo.worktree)
    modified = []
    untracked = []
    deleted = []
    hashes = []

    for file in files:
        hash = plumbing.hash_object("blob", path=file, write=False)
        hashes.append(hash)
        found = False

        for entry in entries:
            if entry.hash != hash and entry.path in file:
                modified.append(entry.path)
                found = True
                break
            elif entry.hash == hash and entry.path in file:
                found = True
                break

        if not found:
            relative_path = os.path.relpath(file, repo.worktree)
            untracked.append(relative_path)

    for entry in entries:
        if entry.hash not in hashes and entry.path not in modified:
            deleted.append(entry.path)

    return {
        "deleted": deleted,
        "modified": modified,
        "untracked": untracked,
    }


def has_uncommited_changes():
    modifies = status()
    return bool(modifies["modified"] or modifies["untracked"] or modifies["deleted"])


def checkout(branch_name, is_new_branch=False):
    """
    Switch branches or restore working tree files
    https://git-scm.com/docs/git-checkout
    """
    repo = find_repository()

    branch_path = repo.worktree + "/" + GITDIR + "/refs/heads/" + branch_name
    with open(repo.build_path("HEAD"), "r+") as file:
        current_branch = file.read().split('/')[-1]

    # Move to an existing branch if it exists
    if is_new_branch:
        if os.path.exists(branch_path):
            print("Branch already exists")
            return

        # Write commit sha1
        current_branch_path = repo.worktree + "/" + GITDIR + "/refs/heads/" + current_branch
        with open(current_branch_path, "r") as file:
            current_branch_commit = file.read()
            with open(branch_path, "w+") as f:
                f.write(current_branch_commit)

        # Switch to new branch
        with open(repo.build_path("HEAD"), "w+") as file:
            file.write(f"ref: refs/heads/{branch_name}")

        print(f"Switched to branch '{branch_name}'")
        return

    if os.path.exists(branch_path):
        STATUS = status()
        # If there are changes, they need to be commited before
        # changing to a branch
        if has_uncommited_changes():
            print_status_messages(STATUS)
        else:
            if current_branch == branch_name:
                print(f"Already on branch {branch_name}")
            else:
                with open(repo.build_path("HEAD"), "r+") as file:
                    file.truncate(0)
                    file.write(f"ref: refs/heads/{branch_name}")
                    plumbing.update_index_entries(branch_path)
                    plumbing.update_working_directory()
                    print(f"Switched to branch {branch_name}")
    else:
        print("Branch does not exist")


def cherry_pick(commit_ref):
    """
    commit_ref: sha1 of commit | branch_name

    Simplified version of cherry pick command.
    We don't handle conflicts yet.

    Given one commit, apply the changes that it introduces recording a new commit.
    This requires your working tree to be clean (no modifications from the HEAD commit).

    https://git-scm.com/docs/git-cherry-pick
    """

    # check if commit_sha1 is a valid sha1 chars with hashlib library
    if is_sha1(commit_ref):
        commit_sha1 = commit_ref
    else:
        # Is a branch name. e.g. feature_branch,
        # we need to get the commit sha1 from refs/heads/feature_branch file.
        commit_sha1 = plumbing.get_reference(f"refs/heads/{commit_ref}")

    if has_uncommited_changes():
        raise Exception("Cannot cherry-pick with uncommited changes")

    repo = find_repository()
    commit_to_cherry_pick = plumbing.get_commit(commit_sha1)

    changes = plumbing.get_commit_changes(commit_sha1)
    for path, sha in changes:
        commited_data = plumbing.cat_file("blob", sha)
        list_path = path.split("/")

        is_modified_file = (
            os.path.exists(path) and plumbing.hash_object("blob", path=path, write=False) != sha
        )
        is_new_file = not os.path.exists(path)

        if is_modified_file or is_new_file:
            # Create paths if not exists
            os.makedirs(os.path.join(repo.worktree, "/".join(list_path[:-1])), exist_ok=True)
            with open(path, "w+") as f:
                # TODO: Check lowest common ancestor hash, to verify if the file has been modified
                # betweet current commit and the lca commit, and detect merge conflicts
                f.write(commited_data)
            add([path])

    return commit(commit_to_cherry_pick.get_message())


def rebase(commit_ref):
    """
    commit_ref: sha1 of commit | branch_name

    Simplified version of rebase command.
    We don't handle conflicts yet.

    Reapply commits on top of another base tip.
    https://git-scm.com/docs/git-rebase
    """

    if is_sha1(commit_ref):
        commit_sha = commit_ref
    else:
        commit_sha = plumbing.get_reference(f"refs/heads/{commit_ref}")

    head_branch = plumbing.get_current_branch()
    current_commit = plumbing.get_reference("HEAD")

    ancestors = ancestors_until_lca(commit_sha, current_commit)[1:]

    if not ancestors:
        print("Cannot rebase a branch onto itself")
        return

    checkout(commit_ref)
    last_commit = None
    for ancestor_hash in ancestors:
        last_commit = cherry_pick(ancestor_hash)

    # Update HEAD with last_commit
    plumbing.update_ref(head_branch, last_commit)
    return last_commit


def log():
    """
    List commits that are reachable by following
    the parent links from the given commit(s)
    https://git-scm.com/docs/git-log
    """

    repo = find_repository()

    head_commit = plumbing.get_reference("HEAD")

    with open(repo.build_path("HEAD"), "r+") as file:
        head = file.read().split('/')[-1]

    head_commit_object: Commit = read_object(repo, head_commit)

    ancestors = get_ancestors(repo, head_commit_object)

    # Print head commit
    log_message = color_text("YELLOW", head_commit[:8]) + color_text("YELLOW", " (")
    log_message += color_text("CYAN", "HEAD ->") + color_text("GREEN", " " + head)
    log_message += color_text("YELLOW", ") ") + head_commit_object.get_message()

    print(log_message)

    for ancestor in ancestors:
        ancestor_commit_obj: Commit = read_object(repo, ancestor)
        print(color_text("YELLOW", ancestor[:8]) + " " + ancestor_commit_obj.get_message())
