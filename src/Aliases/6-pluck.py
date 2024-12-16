import os
import sys
from pathlib import Path

# Local imports
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.Lib.fixture import RepositoryFixture
from src.Lib.verifier import Verify


def heading():
    return 'Git Pluck'

def description():
    return 'Pop a specific stash by index and display the remaining stashes. Without an index argument, it will list the available stashes.'

def command():
    cmd = r"""
    git config --global alias.pluck '!f() {
        if [ -z "$1" ]; then
            if [ -n "$(git stash list)" ]; then
                echo "Available stashes:"
                git stash list
                echo ""
            fi

            printf "Usage: git pluck <index>"
        else
            STASH_INFO=$(git stash list | grep "stash@{$1}")

            if [ -n "$STASH_INFO" ]; then
                echo "Plucking: $STASH_INFO"
            fi

            (git stash pop stash@{$1} 2>&1 |
                grep -A99 "error:" |
                grep -B99 "merge." |
                sed "s/error:/\nerror:/" |
                sed "s/Please/\nPlease/") || true

            if [ -n "$(git stash list)" ]; then
                printf "\nRemaining stashes:"
                printf "\n$(git stash list)"
            fi
        fi
        echo ""
    }; f'
    """
    return cmd.strip()

def example():
    """Get a console output example for the alias."""
    # Setup
    repo = RepositoryFixture('pluck-test')
    repo.run(command())

    # Create stashes for testing
    repo.setup_initial_commit()
    repo.setup_first_stash()
    repo.setup_second_stash()
    repo.setup_third_stash()

    # Get the console output
    output = repo.run("git pluck") + '\n'
    output += repo.run("git pluck 1") + '\n'
    output += repo.run("git pluck 0") + '\n'

    repo.teardown()
    return output.strip()

def test():
    """Test the Git pluck alias."""

    # Setup
    repo = RepositoryFixture('pluck-test')
    repo.run(command())

    # Test the alias without stashes and without an index argument
    output = repo.print('git pluck')
    Verify(output).lacks('Available stashes:')
    Verify(output).contains('Usage: git pluck <index>')

    # create some stashes
    repo.setup_initial_commit()
    repo.setup_first_stash()
    repo.setup_second_stash()
    repo.setup_third_stash()

    # Test the alias with stashes and without an index argument
    output = repo.print("git pluck")
    Verify(output).contains('Available stashes:')
    Verify(output).contains('stash@{0}: On dev: Third Stash')
    Verify(output).contains('stash@{1}: On dev: Second Stash')
    Verify(output).contains('stash@{2}: On dev: First Stash')

    # Apply the changes from the first stash
    output = repo.print("git pluck 2")
    Verify(output).contains('Remaining stashes:')
    Verify(output).contains('Third Stash')
    Verify(output).contains('Second Stash')

    # Verify file-1.txt contains the changes from the first stash
    output = repo.print('cat file-1.txt')
    Verify(output).contains('First revision for file one.')

    # Verify the files contain the changes from the first stash
    output = repo.print('cat file-2.txt')
    Verify(output).contains('First revision for file two.')

    # Try to introduce a conflict and verify the stash won't be applied
    output = repo.print("git pluck 0")
    Verify(output).contains('Your local changes to the following files would be overwritten by merge:')
    Verify(output).contains('file-1.txt')
    Verify(output).contains('file-2.txt')
    Verify(output).contains('Please commit your changes or stash them before you merge.')
    Verify(output).contains('Remaining stashes:')
    Verify(output).contains('stash@{0}: On dev: Third Stash')
    Verify(output).contains('stash@{1}: On dev: Second Stash')

    repo.teardown()

if __name__ == '__main__':
    os.system('clear')

    print('#### Running example() ####\n')
    print(example())

    print('\n#### Running test() ####\n')
    test()
