import collections

from .sha_object import ShaObject


class Commit(ShaObject):
    object_type = b"commit"

    def serialize(self):
        if not self.commit_data:
            return

        raw = b""
        for key, value in self.commit_data.items():
            if key == b"":
                continue

            if not isinstance(value, list):
                value = [value]

            for v in value:
                raw += key + b" " + v + b"\n"

        raw += b"\n" + self.commit_data[b""]
        return raw

    def deserialize(self, data):
        self.commit_data = parse_commit(data)


def parse_commit(raw, start=0, commit_data=None):
    """ """
    if not commit_data:
        commit_data = collections.OrderedDict()

    space = raw.find(b" ", start)
    new_line = raw.find(b"\n", start)

    # If newline appears first (or there's no space at all, in which
    # case find returns -1), we assume a blank line.  A blank line
    # means the remainder of the data is the message.
    if (space < 0) or (new_line < space):
        commit_data[b""] = raw[start + 1 :]
        return commit_data

    key = raw[start:space]
    end = start
    while True:
        end = raw.find(b"\n", end + 1)
        if raw[end + 1] != ord(" "):
            break

    value = raw[space + 1 : end]

    if key in commit_data:
        if isinstance(commit_data[key], list):
            commit_data[key].append(value)
        else:
            commit_data[key] = [commit_data[key], value]
    else:
        commit_data[key] = value
    return parse_commit(raw, start=end + 1, commit_data=commit_data)
