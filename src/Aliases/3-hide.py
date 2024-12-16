import os
import sys
import importlib
from pathlib import Path

# Local imports
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.Lib.fixture import RepositoryFixture
from src.Lib.verifier import Verify


def heading():
    return 'Git Hide'

def description():
    return 'Send unstaged changes to a stash named "hidden". You can add more uncommitted changes to the same stash if needed with the same command.'

def command():
    return r'''
      git config --global alias.hide '!git unhide > /dev/null 2>&1 || true && git stash push --keep-index -m "hidden" > /dev/null && git hidden'
    '''.strip()

def example():
    """Get a console output example for the alias."""
    # Setup the repository
    repo = RepositoryFixture('hide-test')
    repo.run(command())
    repo.setup_initial_commit()
    repo.setup_first_changes()
    repo.stage_file_two()

    # Make sure the hidden alias is available
    module = importlib.import_module('src.Aliases.4-hidden')
    repo.run(module.command())

    # Make sure the unhide alias is available
    module = importlib.import_module('src.Aliases.5-unhide')
    repo.run(module.command())

    # Get the console output
    output = repo.porcelain_status() + "\n"
    output += repo.run("git hide") + "\n"
    output += repo.run("git stash list") + "\n"

    # Add more changes
    repo.setup_second_changes()
    repo.stage_file_two()

    # Demonstrate stashing more changes
    # output += repo.porcelain_status() + "\n"
    output += repo.run('git status --short') + "\n"
    output += repo.run("git hide") + "\n"
    output += repo.run("git stash list") + "\n"

    # Demonstrate unhiding the changes
    output += repo.run("git unhide") + "\n"
    output += repo.run("git stash list")

    repo.teardown()
    return output.strip().replace("\x1b[31m", "").replace("\x1b[32m", "").replace("\x1b[0m", "")

def test():
    """Test the Git hide alias."""

    # Setup
    repo = RepositoryFixture('hide-test')
    repo.run(command())
    repo.setup_initial_commit()
    repo.setup_first_changes()

    # Make sure the hidden alias is available
    module = importlib.import_module('src.Aliases.4-hidden')
    repo.run(module.command())

    print(repo.porcelain_status())

    output = repo.print('cat file-1.txt')
    Verify(output).contains('First revision for file one.')

    output = repo.print('cat file-2.txt')
    Verify(output).contains('First revision for file two.')

    # Hide the changes
    output = repo.print("git hide")
    Verify(output).contains(['Hidden: ', 'file-1.txt'])
    Verify(output).contains(['Hidden: ', 'file-2.txt'])

    output = repo.print('cat file-1.txt')
    Verify(output).contains('Initial change for file one.')

    # Check if the stash is created
    output = repo.print("git stash list")
    Verify(output).contains('stash@{0}: On dev: hidden')

    repo.teardown()

if __name__ == '__main__':
    os.system('clear')

    print('#### Running example() ####\n')
    print(example())

    print('\n#### Running test() ####\n')
    test()
