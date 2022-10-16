from src.repository import create_repository, find_repository


def init(path):
    create_repository(path)


def ls_tree(tree_ish):
    print(tree_ish)
    # repo = find_repository()
    # TODO
    # object = object_find(repo, tree_ish, fmt=b"tree")
    # obj = object_read(repo, object)

    # for item in obj.items:
    #     mode = "0" * (6 - len(item.mode)) + item.mode.decode("ascii")
    #     type = object_read(repo, item.sha).fmt.decode("ascii")
    #     print(f"{mode} {type} {item.sha}\t{item.path.decode('ascii')}")
