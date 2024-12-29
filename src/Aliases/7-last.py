import os
import sys
from pathlib import Path

# Local imports
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.Lib.fixture import RepositoryFixture
from src.Lib.verifier import Verify


def heading():
    return 'Git Last'

def description():
    return '''View recent commits in a clean, terminal-width-aware format.
    - Shows the last 20 commits
    - Truncates to avoid wrapping based on terminal width
    - Adds ellipsis for truncated lines
    '''.strip()

def command():
    return r'''
      git config --global alias.last '!cols=$(tput cols); color_padding=11; git log -n 20 --oneline --color=always | while read -r line; do if [ ${#line} -gt $((cols-3)) ]; then echo "${line:0:$((cols+color_padding-6))}..."; else echo "$line"; fi; done'
    '''.strip()

def example():
    """Get a console output example for the alias."""

    # Setup
    repo = RepositoryFixture('last-test')
    repo.run(command())
    repo.setup_first_commit()
    repo.setup_second_commit()
    message = 'Third committed change. Truncated to fit the terminal width...'
    repo.setup_third_commit(message)

    # Get the console output
    output = repo.run('git last')

    repo.teardown()
    return repo.clean(output)

def test():
    """Test the Git last alias."""
    # Setup the repository
    repo = RepositoryFixture('last-test')
    repo.run(command())
    repo.setup_first_commit()
    repo.setup_second_commit()
    message = 'Third committed change. This commit message is intentionally ' \
      'long to verify that messages exceeding the terminal width are truncated ' \
      'and that the output remains on a single line without wrapping.'
    repo.setup_third_commit(message)

    # Test the alias
    output = repo.print('git last')
    Verify(output).contains('...') # Message is truncated to fit terminal width
    Verify(output).contains('Third committed change')
    Verify(output).contains('Second committed change')
    Verify(output).contains('First committed change')

    repo.teardown()

if __name__ == '__main__':
    os.system('clear')

    print('#### Running example() ####\n')
    print(example())

    print('\n#### Running test() ####\n')
    test()
