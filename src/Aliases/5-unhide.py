import os
import sys
import importlib
from pathlib import Path

# Local imports
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.Lib.fixture import RepositoryFixture
from src.Lib.verifier import Verify


def heading():
    return 'Git Unhide'

def description():
    return '''Restore the hidden changes from the stash named "hidden".
*Not currently working when there is a conflict.*'''

def command():
    cmd = r"""
    git config --global alias.unhide '!f() { files=$(git hidden | sed "s/  Hidden:/  Unhidden:/g" | sed "s/\x1b\[31m/\x1b\[32m/g"); git stash list | grep "hidden" | head -n1 | cut -d: -f1 | xargs -I {} git stash pop {} > /dev/null 2>&1; echo "$files"; }; f'
    """
    return cmd.strip()

def example():
    """Get a console output example for the alias."""

    # Setup
    repo = RepositoryFixture('unhide-test')
    repo.run(command())
    repo.setup_initial_commit()
    repo.setup_first_changes()
    repo.stage_file_two()

    # Make sure the hide alias is available
    module = importlib.import_module('src.Aliases.3-hide')
    repo.run(module.command())

    # Make sure the hidden alias is available
    module = importlib.import_module('src.Aliases.4-hidden')
    repo.run(module.command())

    # Additional setup

    # Hide the changes
    output = repo.porcelain_status() + '\n'
    output += repo.run("git hide") + '\n'
    output += repo.run("git stash list") + '\n'
    output += repo.porcelain_status() + '\n'
    output += repo.run("git unhide") + '\n'
    output += repo.porcelain_status()

    repo.teardown()
    return output.strip().replace("\x1b[31m", "").replace("\x1b[32m", "").replace("\x1b[0m", "")

def test():
    """Test the Git unhide alias."""

    # Setup
    repo = RepositoryFixture('unhide-test')
    repo.run(command())
    repo.setup_initial_commit()
    repo.setup_first_changes()
    repo.stage_file_two()

    # Make sure the hide alias is available
    module = importlib.import_module('src.Aliases.3-hide')
    repo.run(module.command())

    # Make sure the hidden alias is available
    module = importlib.import_module('src.Aliases.4-hidden')
    repo.run(module.command())

    repo.print("git stash list")
    print(repo.porcelain_status())

    repo.print("git hide")
    repo.print("git stash list")
    print(repo.porcelain_status())

    # Unhide the changes
    output = repo.print("git unhide")
    Verify(output).contains(['Unhidden:', 'file-1.txt'])

    repo.print("git stash list")
    print(repo.porcelain_status())

    repo.teardown()

if __name__ == '__main__':
    os.system('clear')

    print('#### Running example() ####\n')
    print(example())

    print('\n#### Running test() ####\n')
    test()
