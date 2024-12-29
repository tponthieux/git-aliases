import os
import sys
from pathlib import Path

# Local imports
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.Lib.fixture import RepositoryFixture
from src.Lib.verifier import Verify


def command():
    cmd = r"""
    git config --global alias.uncommit '!git log -1 --oneline --color=always | sed "s/^/Uncommitted: /" && git reset --soft HEAD~1'
    """
    return cmd.strip()

def heading():
    return "Git Uncommit"

def description():
    return "Undo the last local commit while preserving changes in the working directory without the difficult to remember `git reset --soft HEAD~1`."

def example():
    """Get a console output example for the alias."""

    # Setup the repository and commits and alias
    repo = RepositoryFixture('uncommit-test')
    repo.run(command())
    repo.setup_first_commit()
    repo.setup_second_commit()
    repo.setup_third_commit()

    # Get the console output
    output = repo.run("git log --oneline") + "\n"
    output += repo.run("git uncommit")

    repo.teardown()
    return repo.clean(output)

def test():
    """Test a Git alias."""

    # Setup
    repo = RepositoryFixture('uncommit-test')
    repo.run(command())
    repo.setup_first_commit()
    repo.setup_second_commit()
    repo.setup_third_commit()

    # Verify that there are two commits
    output = repo.print("git log --oneline")
    print(output)
    Verify(output).contains("First committed change")
    Verify(output).contains("Second committed change")
    Verify(output).contains("Third committed change")

    # Run the uncommit alias and verify that the last modified commit was removed
    output = repo.print("git uncommit")
    print(output)
    Verify(output).contains("Third committed change")

    # Check that there are now uncommitted changes
    output = repo.run("git state")
    print(output)
    Verify(output).contains("M  file-1.txt")
    Verify(output).contains("M  file-2.txt")

    # Verify that the uncommitted changes are still there
    output = repo.print("git log --oneline")
    Verify(output).contains("First committed change")
    Verify(output).contains("Second committed change")
    Verify(output).lacks("Third committed change")

    # Run the uncommit alias and verify that the last modified commit was removed
    output = repo.print("git uncommit")
    Verify(output).contains("Second committed change")

    # Verify that the uncommitted changes are still there
    output = repo.print("git log --oneline")
    Verify(output).contains("First committed change")
    Verify(output).lacks("Second committed change")
    Verify(output).lacks("Third committed change")

    # Check that there are still uncommitted changes
    output = repo.run("git state")
    print(output)
    Verify(output).contains("M  file-1.txt")
    Verify(output).contains("M  file-2.txt")
    repo.print("cat file-1.txt")
    repo.print("cat file-2.txt")

    repo.teardown()

if __name__ == "__main__":
    os.system('clear')

    print('#### Running example() ####\n')
    print(example())

    print('\n#### Running test() ####\n')
    test()
