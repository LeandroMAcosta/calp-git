# Test file
import os
import unittest

from src.index import read_entries

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
