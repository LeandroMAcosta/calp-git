import os
from typing import List

from src.index import IndexEntry, read_entries, write_entries
from src.plumbing import (get_commit_sha1, hash_object, read_object,
                          update_current_ref, write_commit, write_tree,
                          update_index_entries, update_working_directory)
from src.repository import GITDIR, create_repository, find_repository
from src.utils import get_files_rec, print_status_messages


def init(path):
    create_repository(path)


def add(paths):
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
            hash = hash_object("blob", path=path, write=True)
            entry = IndexEntry(path, hash)
            entries.append(entry)

    write_entries(entries)


def commit(message):
    tree_sha1 = write_tree()

    parent = get_commit_sha1("HEAD")

    if parent:
        repo = find_repository()
        current_commit = read_object(repo, parent)
        data = current_commit.commit_data
        if data[b"tree"] == tree_sha1.encode("ascii"):
            print("Nothing to commit")
            return
        commit_sha1 = write_commit(tree_sha1, message, [parent])
    else:
        commit_sha1 = write_commit(tree_sha1, message)

    # HEAD apunta a un commit (sha1)
    # - Actualizar HEAD al commit nuevo
    # HEAD apunta a una branch (ref: refs/heads/master)
    # - Actualizar refs/heads/master al commit nuevo
    update_current_ref(commit_sha1)
    return commit_sha1


def status():
    # Read the entries from the staging area in the index file
    entries: List[IndexEntry] = read_entries()
    repo = find_repository()
    files = get_files_rec(repo.worktree)
    modified = []
    untracked = []
    deleted = []
    hashes = []

    for file in files:
        hash = hash_object("blob", path=file, write=False)
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


def checkout(is_new_branch, args):
    repo = find_repository()

    branch_name = args[0]
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
            current_branch_commit =  file.read()
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
        if STATUS["deleted"] or STATUS["modified"] or STATUS["untracked"]:
            print_status_messages(STATUS)
        else:
            if current_branch == branch_name:
                print(f"Already on branch {branch_name}")
            else:
                with open(repo.build_path("HEAD"), "r+") as file:
                    file.truncate(0)
                    file.write(f"ref: refs/heads/{branch_name}")
                    update_index_entries(branch_path)
                    update_working_directory()
                    print(f"Switched to branch {branch_name}")
    else:
        print("Branch does not exist")
    return 