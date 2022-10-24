# Test file
import io
import os
import sys
import unittest
from contextlib import suppress

from src.index import read_entries
from src.plumbing import (get_commit_changes, get_reference, read_object,
                          write_tree)
from src.porcelain import status
from src.repository import find_repository

TEST_PATHS = f"{os.getcwd()}/tests"
ABSOLUTE_PATH = f"{TEST_PATHS}/tmp"
GITDIR = ".calp"


print("Running tests...")
if not os.path.exists(ABSOLUTE_PATH):
    os.mkdir(f"{ABSOLUTE_PATH}/")


class TestGitCommands(unittest.TestCase):

    def setUp(self):
        os.system(f"rm -rf {ABSOLUTE_PATH}/*")
        return super().setUp()

    def tearDown(self):
        os.system(f"rm -rf {ABSOLUTE_PATH}/*")
        os.system(f"rm -rf {ABSOLUTE_PATH}/{GITDIR}")

    def test_init(self):

        # assert that tmp_path not exists
        self.assertTrue(os.path.exists(ABSOLUTE_PATH))
        os.chdir(ABSOLUTE_PATH)

        # execute bash command ../calp init .
        self.assertFalse(os.path.exists(f"{ABSOLUTE_PATH}/{GITDIR}"))
        self.assertFalse(os.path.exists(f"{ABSOLUTE_PATH}/{GITDIR}/HEAD"))
        self.assertFalse(os.path.exists(f"{ABSOLUTE_PATH}/{GITDIR}/objects"))
        self.assertFalse(os.path.exists(f"{ABSOLUTE_PATH}/{GITDIR}/refs"))
        os.system("../../calp init")

        # assert that .git directory exists
        self.assertTrue(os.path.exists(f"{ABSOLUTE_PATH}/{GITDIR}"))
        self.assertTrue(os.path.exists(f"{ABSOLUTE_PATH}/{GITDIR}/HEAD"))
        self.assertTrue(os.path.exists(f"{ABSOLUTE_PATH}/{GITDIR}/objects"))
        self.assertTrue(os.path.exists(f"{ABSOLUTE_PATH}/{GITDIR}/refs"))

    def test_add(self):
        # assert that tmp_path not exists
        self.assertTrue(os.path.exists(ABSOLUTE_PATH))
        os.chdir(ABSOLUTE_PATH)

        # execute bash command ../calp init .
        os.system("../../calp init")

        # create file
        os.system("echo 'test' > test.txt")
        expected_hash = "9daeafb9864cf43055ae93beb0afd6c7d144bfa4"

        # execute bash command ../calp add .
        os.system("../../calp add test.txt")
        expected_path = (
            f"{ABSOLUTE_PATH}/{GITDIR}/objects/{expected_hash[:2]}/{expected_hash[2:]}"
        )
        self.assertTrue(os.path.exists(expected_path))

    def test_add_deleted_file(self):
        # assert that tmp_path not exists
        self.assertTrue(os.path.exists(ABSOLUTE_PATH))
        os.chdir(ABSOLUTE_PATH)

        # execute bash command ../calp init .
        os.system("../../calp init")

        # create file
        os.system("echo 'test' > test.txt")
        os.system("echo 'test1' > test1.txt")
        os.system("echo 'test2' > test2.txt")

        expected_hash = "9daeafb9864cf43055ae93beb0afd6c7d144bfa4"

        # execute bash command ../calp add .
        os.system("../../calp add test.txt test1.txt test2.txt")
        expected_path = (
            f"{ABSOLUTE_PATH}/{GITDIR}/objects/{expected_hash[:2]}/{expected_hash[2:]}"
        )
        self.assertTrue(os.path.exists(expected_path))

        entries = read_entries()
        self.assertEqual(len(entries), 3)

        # delete file
        os.system("rm test.txt")
        self.assertFalse(os.path.exists("test.txt"))
        os.system("../../calp add test.txt")

        # assert that file was deleted from staging area
        entries = read_entries()
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0].path, "test1.txt")
        self.assertEqual(entries[0].hash, "a5bce3fd2565d8f458555a0c6f42d0504a848bd5")
        self.assertEqual(entries[1].path, "test2.txt")
        self.assertEqual(entries[1].hash, "180cf8328022becee9aaa2577a8f84ea2b9f3827")

    def test_status_untracked(self):
        # assert that tmp_path not exists
        self.assertTrue(os.path.exists(ABSOLUTE_PATH))
        os.chdir(ABSOLUTE_PATH)

        # execute bash command ../calp init .
        os.system("../../calp init")

        # create file
        os.system("echo 'test' > test.txt")
        expected_hash = "9daeafb9864cf43055ae93beb0afd6c7d144bfa4"

        STATUS = status()
        self.assertTrue("test.txt" in STATUS["untracked"])
        self.assertTrue(STATUS["deleted"] == [])
        self.assertTrue(STATUS["modified"] == [])

        # execute bash command ../calp add .
        os.system("../../calp add test.txt")
        expected_path = (
            f"{ABSOLUTE_PATH}/{GITDIR}/objects/{expected_hash[:2]}/{expected_hash[2:]}"
        )
        self.assertTrue(os.path.exists(expected_path))

        STATUS = status()
        self.assertTrue(STATUS["untracked"] == [])
        self.assertTrue(STATUS["deleted"] == [])
        self.assertTrue(STATUS["modified"] == [])

    def test_status_deleted(self):
        # assert that tmp_path not exists
        self.assertTrue(os.path.exists(ABSOLUTE_PATH))
        os.chdir(ABSOLUTE_PATH)

        # execute bash command ../calp init .
        os.system("../../calp init")

        # create file
        os.system("echo 'test' > test.txt")
        expected_hash = "9daeafb9864cf43055ae93beb0afd6c7d144bfa4"

        STATUS = status()
        self.assertTrue("test.txt" in STATUS["untracked"])
        self.assertTrue(STATUS["deleted"] == [])
        self.assertTrue(STATUS["modified"] == [])

        # execute bash command ../calp add .
        os.system("../../calp add test.txt")
        expected_path = (
            f"{ABSOLUTE_PATH}/{GITDIR}/objects/{expected_hash[:2]}/{expected_hash[2:]}"
        )
        self.assertTrue(os.path.exists(expected_path))

        os.system("rm test.txt")

        STATUS = status()
        self.assertTrue(STATUS["untracked"] == [])
        self.assertTrue("test.txt" in STATUS["deleted"])
        self.assertTrue(STATUS["modified"] == [])

    def test_status_modified(self):
        # assert that tmp_path not exists
        self.assertTrue(os.path.exists(ABSOLUTE_PATH))
        os.chdir(ABSOLUTE_PATH)

        # execute bash command ../calp init .
        os.system("../../calp init")

        # create file
        os.system("echo 'test' > test.txt")
        expected_hash = "9daeafb9864cf43055ae93beb0afd6c7d144bfa4"

        STATUS = status()
        self.assertTrue("test.txt" in STATUS["untracked"])
        self.assertTrue(STATUS["deleted"] == [])
        self.assertTrue(STATUS["modified"] == [])

        # execute bash command ../calp add .
        os.system("../../calp add test.txt")
        expected_path = (
            f"{ABSOLUTE_PATH}/{GITDIR}/objects/{expected_hash[:2]}/{expected_hash[2:]}"
        )
        self.assertTrue(os.path.exists(expected_path))

        os.system("echo 'test1' > test.txt")

        STATUS = status()
        self.assertTrue(STATUS["untracked"] == [])
        self.assertTrue(STATUS["deleted"] == [])
        self.assertTrue("test.txt" in STATUS["modified"])

    def test_commit(self):
        # assert that tmp_path not exists
        self.assertTrue(os.path.exists(ABSOLUTE_PATH))
        os.chdir(ABSOLUTE_PATH)

        # execute bash command ../calp init .
        os.system("../../calp init")

        # create file
        os.system("echo 'main' > main.txt")
        os.system("mkdir A")
        os.system("echo 'testing' > A/file.txt")

        expected_hash_main = "ba2906d0666cf726c7eaadd2cd3db615dedfdf3a"
        expected_hash_file = "038d718da6a1ebbc6a7780a96ed75a70cc2ad6e2"

        os.system("../../calp add main.txt A/file.txt")
        expected_path_main = f"{ABSOLUTE_PATH}/{GITDIR}/objects/{expected_hash_main[:2]}/{expected_hash_main[2:]}"
        expected_path_file = f"{ABSOLUTE_PATH}/{GITDIR}/objects/{expected_hash_file[:2]}/{expected_hash_file[2:]}"
        self.assertTrue(os.path.exists(expected_path_main))
        self.assertTrue(os.path.exists(expected_path_file))

        os.system("../../calp commit -m 'first commit'")

        expected_hash_A_dir = "b06a41c2dded8f7ce5b7341decbf5a89a42c9302"
        expected_path_A_dir = f"{ABSOLUTE_PATH}/{GITDIR}/objects/{expected_hash_A_dir[:2]}/{expected_hash_A_dir[2:]}"
        self.assertTrue(os.path.exists(expected_path_A_dir))

        repo = find_repository()
        tree_hash = write_tree()
        commit_sha = get_reference("HEAD")
        commit = read_object(repo, commit_sha)
        self.assertTrue(commit.commit_data[b"tree"] == tree_hash.encode("ascii"))

    def test_commit_differences(self):
        # assert that tmp_path not exists
        self.assertTrue(os.path.exists(ABSOLUTE_PATH))
        os.chdir(ABSOLUTE_PATH)

        # execute bash command ../calp init .
        os.system("../../calp init")

        # create file
        os.system("echo 'main' > main.txt")
        os.system("../../calp add main.txt")
        os.system("../../calp commit -m 'first commit'")
        first_commit_sha1 = get_reference("HEAD")

        os.system("mkdir A")
        os.system("echo 'testing' > A/file.txt")
        os.system("../../calp add A/file.txt")
        os.system("../../calp commit -m 'second commit'")
        second_commit_sha1 = get_reference("HEAD")

        self.assertTrue(first_commit_sha1 != second_commit_sha1)
        changes = list(get_commit_changes(second_commit_sha1))
        self.assertTrue(changes[0][0] == "A/file.txt")
        self.assertTrue(changes[0][1] == "038d718da6a1ebbc6a7780a96ed75a70cc2ad6e2")
        self.assertTrue(len(changes) == 1)

    def test_checkout_new_branch_ok(self):
        # assert that tmp_path not exists
        self.assertTrue(os.path.exists(ABSOLUTE_PATH))
        os.chdir(ABSOLUTE_PATH)
        # execute bash command ../calp init .
        os.system("../../calp init")
        os.system("echo 'main' > main.txt")
        os.system("../../calp add main.txt")
        os.system("../../calp commit -m 'first commit'")
        os.system("../../calp checkout -b new_branch")
        expected_path = (
            f"{ABSOLUTE_PATH}/{GITDIR}/refs/heads/new_branch"
        )
        self.assertTrue(os.path.exists(expected_path))
        with open(f"{ABSOLUTE_PATH}/{GITDIR}/HEAD", 'r') as file:
            branch = file.read().split('/')[-1]
            self.assertEqual(branch, 'new_branch')

    def test_checkout_failed(self):
        # assert that tmp_path not exists
        self.assertTrue(os.path.exists(ABSOLUTE_PATH))
        os.chdir(ABSOLUTE_PATH)
        # execute bash command ../calp init .
        os.system("../../calp init")
        os.system("../../calp checkout fake_branch")
        with open(f"{ABSOLUTE_PATH}/{GITDIR}/HEAD", 'r') as file:
            branch = file.read().split('/')[-1]
            self.assertEqual(branch, 'master')

    def test_checkout_verify_index_update(self):
        # assert that tmp_path not exists
        self.assertTrue(os.path.exists(ABSOLUTE_PATH))
        os.chdir(ABSOLUTE_PATH)
        # execute bash command ../calp init .
        os.system("../../calp init")
        os.system("echo 'main' > main.txt")
        correct_data = ""
        with open(f"{ABSOLUTE_PATH}/main.txt") as file:
            correct_data = file.read()
        os.system("../../calp add main.txt")
        os.system("../../calp commit -m 'first commit'")
        os.system("../../calp checkout -b new_branch")
        with open(f"{ABSOLUTE_PATH}/{GITDIR}/HEAD", 'r') as file:
            branch = file.read().split('/')[-1]
            self.assertEqual(branch, 'new_branch')
        os.system("echo 'naim' > main.txt")
        with open(f"{ABSOLUTE_PATH}/main.txt") as file:
            self.assertNotEqual(correct_data, file.read())
        os.system("../../calp add main.txt")
        os.system("../../calp commit -m 'second commit'")
        os.system("../../calp checkout master")
        with open(f"{ABSOLUTE_PATH}/{GITDIR}/HEAD", 'r') as file:
            branch = file.read().split('/')[-1]
            self.assertEqual(branch, 'master')
        with open(f"{ABSOLUTE_PATH}/main.txt") as file:
            self.assertEqual(correct_data, file.read())

    def test_cherry_pick(self):
        self.assertTrue(os.path.exists(ABSOLUTE_PATH))
        os.chdir(ABSOLUTE_PATH)

        os.system("../../calp init")

        os.system("echo '1' > 1.txt")
        os.system("../../calp add 1.txt")       # d00491fd7e5bb6fa28c517a0bb32b8b506539d4d
        os.system("../../calp commit -m 'a'")

        os.system("echo '2' > 2.txt")            # 0cfbf08886fca9a91cb753ec8734c84fcbe52c9f
        os.system("../../calp add 2.txt")
        os.system("../../calp commit -m 'b'")
        commit_sha_main = get_reference("HEAD")

        # Simulate calp checkout -b feature
        os.system("cat .calp/refs/heads/master | { read commit; echo $commit > .calp/refs/heads/feature; }")
        os.system("echo 'ref: refs/heads/feature' > .calp/HEAD")
        commit_sha_feature = get_reference("HEAD")

        self.assertTrue(commit_sha_main == commit_sha_feature)

        os.system("echo '3' > 3.txt")        # 00750edc07d6415dcc07ae0351e9397b0222b7ba
        os.system("echo 'new 2' > 2.txt")    # aef0730e4d285b798126f52c07a06b9efd1a3c9d
        os.system("../../calp add 2.txt 3.txt")
        os.system("../../calp commit -m 'c'")

        # Simulate calp checkout master
        os.system("echo 'ref: refs/heads/master' > .calp/HEAD")
        self.assertTrue(get_reference("refs/heads/master") == commit_sha_main)

        os.system("echo '2' > 2.txt")        # 0cfbf08886fca9a91cb753ec8734c84fcbe52c9f
        os.system("rm 3.txt")
        expected_index = "echo 'd00491fd7e5bb6fa28c517a0bb32b8b506539d4d 1.txt\n"
        expected_index += "0cfbf08886fca9a91cb753ec8734c84fcbe52c9f 2.txt' > .calp/index"
        os.system(expected_index)

        os.system("../../calp cherry-pick feature")

        entries = read_entries()

        self.assertTrue(len(entries) == 3)
        self.assertTrue(entries[0].path == "1.txt")
        self.assertTrue(entries[1].path == "2.txt")
        self.assertTrue(entries[2].path == "3.txt")

        repo = find_repository()
        obj = read_object(repo, entries[1].hash)
        self.assertTrue(obj.blob_data == b"new 2\n")

        obj = read_object(repo, entries[2].hash)
        self.assertTrue(obj.blob_data == b"3\n")
