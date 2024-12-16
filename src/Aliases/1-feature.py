import os
import sys
from pathlib import Path

# Local imports
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.Lib.fixture import RepositoryFixture
from src.Lib.verifier import Verify


def heading():
    return "Git Feature"

def description():
    return "Create a new feature branch from the current branch with a random identifier. Note that it relies on dashes as a delimiter, so it can't be used if your branch names include dashes."

def command():
    cmd = r"""
    git config --global alias.feature '!git status --short && git checkout -b feature-$(git branch --show-current)-$(openssl rand -hex 4) 2>&1'
    """
    return cmd.strip()

def example():
    """Get a console output example for the alias."""
    # Setup
    repo = RepositoryFixture('feature-test')
    repo.setup_first_commit()
    repo.setup_second_changes()
    repo.stage_file_two()
    repo.run(command())

    # Get the console output
    output = repo.run("git branch") + "\n"
    output += repo.run("git feature") + "\n"
    output += repo.run("git branch")

    repo.teardown()
    return output.strip()

def test():
    """Test the Git feature alias."""

    # Setup the repository
    repo = RepositoryFixture('feature-test')
    repo.setup_first_commit()
    repo.setup_second_changes()
    repo.stage_file_two()
    repo.run(command())

    # Create a feature branch
    output = repo.print("git feature")
    Verify(output).contains(" M file-1.txt")
    Verify(output).contains("M  file-2.txt")
    Verify(output).contains("Switched to a new branch 'feature-dev-")

    repo.teardown()

if __name__ == "__main__":
    os.system('clear')

    print('#### Running example() ####\n')
    print(example())

    print('\n#### Running test() ####\n')
    test()
