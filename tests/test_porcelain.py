# Test file
import os
import unittest

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
