from typing import Dict, List

from .base import BaseObject


class TreeLeaf:
    # Format: [mode] space [path] 0x00 [sha-1]
    def __init__(self, mode, path, sha, length):
        self.mode = mode
        self.path = path
        self.sha = sha
        self.length = length


class Tree(BaseObject):
    """
    Format of a tree object:
    tree {size}\0
    {mode} {path_1}\0{sha-1}
    {mode} {path_2}\0{sha-1}
    ...
    {mode} {path_n}\0{sha-1}

    links:
    https://git-scm.com/book/en/v2/Git-Internals-Git-Objects
    https://stackoverflow.com/questions/14790681/what-is-the-internal-format-of-a-git-tree-object
    """

    object_type = b"tree"

    def deserialize(self, data):
        self.items = self.parse_tree(data)

    def serialize(self) -> bytes:
        ret = b""
        for item in self.items:
            sha = int(item.sha, 16).to_bytes(20, byteorder="big")
            raw = item.mode + b" " + item.path + b"\x00" + sha
            ret += raw
        return ret

    def parse_tree(self, data) -> List[TreeLeaf]:
        pos = 0
        max = len(data)
        ret = []
        while pos < max:
            # Find raw
            end_of_raw = data.find(b"\x00", pos) + 20  # 20 is the length of sha-1
            raw = data[pos : end_of_raw + 1]
            leaf: TreeLeaf = parse_to_leaf(raw)
            pos = end_of_raw + 1
            ret.append(leaf)

        return ret


def parse_to_leaf(raw: bytes) -> TreeLeaf:
    start = 0
    # Find the space terminator of the mode
    x = raw.find(b" ", start)
    assert 5 <= x - start <= 6
    # TODO: revisra el start
    mode = raw[:x]

    # Find the NULL terminator of the path
    y = raw.find(b"\x00", x)
    path = raw[x + 1 : y]

    # Read the SHA and convert to an hex string
    sha = raw[y + 1 :]
    assert len(sha) == 20
    parsed_sha1 = hex(int.from_bytes(sha, "big"))[2:]
    if len(parsed_sha1) < 40:
        """
        The hex representation of a SHA-1 hash is 40 characters long.
        If the hex representation is shorter than 40 characters, it is
        left-padded with zeros.
        e.g. If the original sha1 starts with 0x038.... then
        parsed_sha1 starts with 38, so we have to add 0s to the left
        """
        parsed_sha1 = "0" * (40 - len(parsed_sha1)) + parsed_sha1

    return TreeLeaf(mode, path, parsed_sha1, y + 21)


# recursive tree parsing
def create_tree_file(entries: dict) -> Tree:
    ...
