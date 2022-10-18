# Test file
import os
import unittest

TEST_PATHS = os.getcwd()
ABSOLUTE_PATH = f"{TEST_PATHS}/tmp"
GITDIR = ".calp"


def clean_tmp():
    os.system(f"rm -rf {ABSOLUTE_PATH}/*")
    os.system(f"rm -rf {ABSOLUTE_PATH}/{GITDIR}")


class TestGitCommands(unittest.TestCase):
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

        clean_tmp()

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
        clean_tmp()


if __name__ == "__main__":
    if not os.path.exists(ABSOLUTE_PATH):
        os.mkdir(ABSOLUTE_PATH)
    print(ABSOLUTE_PATH)
    unittest.main()
    clean_tmp()
