import os
import sys
from pathlib import Path

# Local imports
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.Lib.fixture import RepositoryFixture
from src.Lib.verifier import Verify


def heading():
    return "Git Aliases"

def description():
    return "List all of the available Git aliases."

def command():
    cmd = r'''
      git config --global alias.aliases '!printf "Available Commands:\n" && git config --get-regexp alias | grep "^alias\." | awk -F"[. ]" "{print \"  git \" \$2}"'
    '''
    return cmd.strip()

def example():
    """Get a console output example for the alias."""
    # Setup
    repo = RepositoryFixture('aliases-test')

    # Get the console output
    output = repo.run("git aliases")

    repo.teardown()
    return repo.clean(output)

def test():
    """Test a Git alias."""
    # Setup
    repo = RepositoryFixture('aliases-test')
    repo.run(command())

    # Test the alias
    output = repo.print("git aliases")
    Verify(output).contains("Available Commands:")
    Verify(output).contains("  git aliases")
    Verify(output).lacks("bogus")

    repo.teardown()

if __name__ == "__main__":
    os.system('clear')

    print('#### Running example() ####\n')
    print(example())

    print('\n#### Running test() ####\n')
    test()
