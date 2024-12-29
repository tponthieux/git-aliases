import os
import sys
import importlib
from pathlib import Path

# Local imports
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.Lib.fixture import RepositoryFixture
from src.Lib.verifier import Verify


def heading():
    return 'Git Hidden'

def description():
    return 'List the file names for changes stored in a stash named "hidden".'

def command():
    cmd = r"""
    git config --global alias.hidden '!git stash list | grep ": hidden" | head -n1 | cut -d: -f1 | xargs -I {} git show --pretty="" --name-only {} | while read file; do echo "  Hidden: \033[31m$file\033[0m"; done'
    """
    return cmd.strip()

def example():
    """Get a console output example for the alias."""
    # Setup the repository
    repo = RepositoryFixture('hidden-test')
    repo.setup_first_commit()
    # repo.setup_second_commit()
    repo.run(command())

    # Add the hide alias dependency
    module = importlib.import_module('src.Aliases.3-hide')
    repo.run(module.command())

    # Create some changes and stash them
    repo.write_file('file-1.txt', 'Unstaged change for file one.\n')
    repo.write_file('file-2.txt', 'Unstaged change for file two.\n')

    # Get the console output
    output = repo.run("git state") + '\n'
    output += repo.run('git add file-2.txt') + '\n'
    output += repo.run("git state") + '\n'
    output += repo.run("git hide") + '\n'
    output += repo.run("git state") + '\n'
    output += repo.run("git stash list") + '\n'
    output += repo.run("git hidden")

    repo.teardown()
    return repo.clean(output)

def test():
    """Test the Git hidden alias."""

    # Setup
    repo = RepositoryFixture('hidden-test')
    repo.run(command())
    repo.setup_initial_commit()
    repo.setup_first_changes()
    repo.run('git stash push --keep-index -m "hidden"')

    # Add the hide alias dependency
    module = importlib.import_module('src.Aliases.3-hide')
    repo.run(module.command())

    # Run the hidden alias
    output = repo.print("git hidden")
    Verify(output).contains('Hidden: file-1.txt')
    Verify(output).contains('Hidden: file-2.txt')

    output = repo.print("git stash list")
    Verify(output).contains('hidden')

    repo.teardown()

if __name__ == '__main__':
    os.system('clear')

    print('#### Running example() ####\n')
    print(example())

    print('\n#### Running test() ####\n')
    test()
