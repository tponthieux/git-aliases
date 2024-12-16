import re
class Verify(str):
    """A string like class for verifying the contents of a command result."""

    def contains(self, expectation):
        pattern = '.*'.join(map(re.escape, expectation))
        if not re.search(pattern, self):
            raise AssertionError(f'The value {self.fmt()}does not contain "{expectation}".\n')

    def lacks(self, expectation):
        pattern = '.*'.join(map(re.escape, expectation))
        if re.search(pattern, self):
            raise AssertionError(f'The value {self.fmt()}does contain "{expectation}".\n')

    def fmt(self):
        if '\n' in self:
            return f'\n```\n{self}\n```\n'
        return f'`{self}` '


if __name__ == "__main__":
    import os
    os.system('clear')

    # Does contain
    Verify("ABC\n123").contains("ABC")
    Verify("ABC\n123").contains("123")
    Verify("ABC\n123").contains(["A", "C"])
    Verify("ABC\n123").contains(["1", "3"])

    try:
        Verify("ABC\n123").lacks("ABC")
    except AssertionError as e:
        print(f'Error: {e}')

    try:
        Verify("ABC\n123").lacks("123")
    except AssertionError as e:
        print(f'Error: {e}')

    try:
        Verify("ABC\n123").lacks(["A", "C"])
    except AssertionError as e:
        print(f'Error: {e}')

    try:
        Verify("ABC\n123").lacks(["1", "3"])
    except AssertionError as e:
        print(f'Error: {e}')

    # Does not contain
    Verify("ABC\n123").lacks("XYZ")
    Verify("ABC\n123").lacks(["B", "2"])
    Verify("ABC\n123").lacks(["1", "4"])

    try:
        Verify("ABC\n123").contains("XYZ")
    except AssertionError as e:
        print(f'Error: {e}')

    try:
        Verify("ABC\n123").contains(["B", "2"])
    except AssertionError as e:
        print(f'Error: {e}')

    try:
        Verify("ABC\n123").contains(["1", "4"])
    except AssertionError as e:
        print(f'Error: {e}')
