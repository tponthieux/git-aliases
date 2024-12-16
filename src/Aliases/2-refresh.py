import os
import sys
from pathlib import Path

# Local imports
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.Lib.fixture import RepositoryFixture
from src.Lib.verifier import Verify


def heading():
    return "Git Refresh"

def description():
    return "This is intended to be used after the feature branch generated via the 'git feature' alias has been merged on the remote repository. This command will temporarily stash changes (if any), switch back to the original branch, pull the latest changes, delete any local branches prefixed with \"feature-\", and reapply the temporarily stashed changes."

def command():
    cmd = r"""
    git config --global alias.refresh '!branch=$(git branch --show-current); original_branch=$(echo $branch | cut -d"-" -f2); git stash && git checkout $original_branch && git pull && git branch | grep "feature-" | xargs git branch -D && git stash pop && git branch'
    """
    return cmd.strip()

def example():
    """Get a console output example for the alias."""

    # Setup the remote repository first
    remote = RepositoryFixture('refresh-remote')
    remote.run(command())
    remote.setup_first_commit()
    remote_path = remote.path.absolute()

    # Create local repo and copy .git from remote
    local = RepositoryFixture('refresh-local')
    local_path = local.path.absolute()
    local.run(f'rm -rf "{local_path}/.git"')
    local.run(f'cp -r "{remote_path}/.git" "{local_path}/.git"')
    local.run('git reset --hard HEAD')

    # Setup remote tracking on the local repository
    local.run(f'git remote add origin "{remote_path}"')
    local.run('git fetch origin')
    local.run("git branch --set-upstream-to=origin/dev dev")

    # Create a feature branch on local and push it to remote
    local.print("git branch")
    local.print("git checkout -b feature-dev-0dc6a7a1 dev")
    local.print("git branch")
    local.setup_second_commit()
    local.run("git push --set-upstream origin feature-dev-0dc6a7a1")

    # Merge the feature branch on the remote repository
    remote.print("git merge --ff-only feature-dev-0dc6a7a1")

    # Refresh local
    local.setup_third_changes()
    output = local.run("git refresh")

    local.teardown()
    remote.teardown()
    return output.strip()

def test():
    """Test the Git refresh alias."""

    # Setup the remote repository first
    remote = RepositoryFixture('refresh-remote')
    remote.run(command())
    remote.setup_first_commit()
    remote_path = remote.path.absolute()

    # Create local repo and copy .git from remote
    local = RepositoryFixture('refresh-local')
    local_path = local.path.absolute()
    local.run(f'rm -rf "{local_path}/.git"')
    local.run(f'cp -r "{remote_path}/.git" "{local_path}/.git"')
    local.run('git reset --hard HEAD')

    # Setup remote tracking on the local repository
    local.run(f'git remote add origin "{remote_path}"')
    local.run('git fetch origin')
    local.run("git branch --set-upstream-to=origin/dev dev")

    # Create a feature branch on local and push it to remote
    local.print("git branch")
    local.print("git checkout -b feature-dev-0dc6a7a1 dev")
    local.print("git branch")
    local.setup_second_commit()
    local.run("git push --set-upstream origin feature-dev-0dc6a7a1")

    # Merge the feature branch on the remote repository
    remote.print("git merge --ff-only feature-dev-0dc6a7a1")

    # Refresh local
    local.setup_third_changes()
    output = local.print("git refresh")

    # Verify the output
    Verify(output).contains("Saved working directory and index state WIP on feature-dev-")
    Verify(output).contains("Second committed change")
    Verify(output).contains("Your branch is up to date with 'origin/dev'.")
    Verify(output).contains("Updating ")
    Verify(output).contains("Fast-forward")
    Verify(output).contains(" file-1.txt | 2 +-")
    Verify(output).contains(" file-2.txt | 2 +-")
    Verify(output).contains(" 2 files changed, 2 insertions(+), 2 deletions(-)")
    Verify(output).contains("Deleted branch feature-dev-")
    Verify(output).contains("On branch dev")
    Verify(output).contains("Your branch is up to date with 'origin/dev'.")
    Verify(output).contains("Changes not staged for commit:")
    Verify(output).contains("(use \"git add <file>...\" to update what will be committed)")
    Verify(output).contains("(use \"git restore <file>...\" to discard changes in working directory)")
    Verify(output).contains("modified:   file-1.txt")
    Verify(output).contains("modified:   file-2.txt")
    Verify(output).contains("no changes added to commit (use \"git add\" and/or \"git commit -a\")")
    Verify(output).contains("Dropped refs/stash@{0}")
    Verify(output).contains("* dev")

    local.teardown()
    remote.teardown()

if __name__ == "__main__":
    os.system('clear')

    print('#### Running example() ####\n')
    print(example())

    print('\n#### Running test() ####\n')
    test()