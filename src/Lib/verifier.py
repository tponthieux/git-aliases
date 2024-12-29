import re

class Verify(str):
    """Provides methods to check if command output contains or lacks certain
    text patterns. Formats error messages with code blocks for readability."""

    def contains(self, expectation):
        """Check that the string contains the expected patterns in sequence on a single line."""

        pattern = '.*'.join(map(re.escape, expectation))
        if not re.search(pattern, self):
            raise AssertionError(f'The value {self.fence()}does not contain "{expectation}".\n')

    def lacks(self, expectation):
        """Check that the string does not contain the expected patterns on a single line."""

        pattern = '.*'.join(map(re.escape, expectation))
        if re.search(pattern, self):
            raise AssertionError(f'The value {self.fence()}does contain "{expectation}".\n')

    def fence(self):
        """Format the string as a fenced code block for error message readability."""
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
