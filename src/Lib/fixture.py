import os
import shutil
import subprocess

from pathlib import Path

BRACKETS = False

class RepositoryFixture:
    """Creates an isolated Git repository for testing Git aliases and commands.
    Handles setup, manipulation and teardown of the test repository."""

    def __init__(self, name):
        self.path = Path('repos', name)
        self.setup()

    def setup(self):
        """Set up a Git repository for testing."""
        if os.path.exists(self.path):
            shutil.rmtree(self.path)

        os.makedirs(self.path, exist_ok=True)
        self.run("git init")
        self.run("git branch -M dev")

    def teardown(self):
        """Clean up the temporary repository."""
        if os.path.exists(self.path.parent):
            shutil.rmtree(self.path.parent)

    def run(self, cmd):
        """Run a git command in this repository and return the output."""
        env = os.environ.copy()
        env.update({
            'COLUMNS': str(shutil.get_terminal_size().columns) # Set terminal width
        })
        result = subprocess.run(cmd, cwd=self.path, text=True, shell=True, capture_output=True, env=env)

        if result.returncode != 0:
            error_msg = f"Command failed with exit code {result.returncode}\n$ {cmd}"
            if result.stdout:
                error_msg += f"\nstdout:\n{result.stdout}"
            if result.stderr:
                error_msg += f"\nstderr:\n{result.stderr}"
            raise RuntimeError(error_msg)

        if result.stdout.endswith('\n\n'):
            raise RuntimeError(
                f"$ {cmd}\n{result.stdout}"
                f"Command output has extra trailing newlines."
                )

        # if not result.stdout.endswith('\n'):
        #     raise RuntimeError(
        #         f"$ {cmd}\n{result.stdout}"
        #         f"Command output does not end with a newline."
        #         )

        output = f'$ {cmd}\n{result.stdout}'
        output = output if output.endswith('\n') else output + '\n'

        return f'[{output}]' if BRACKETS else output

    def print(self, cmd):
        """Run a command in this repository and print the output."""
        output = self.run(cmd)
        print(output)
        return output

    def clean(self, output):
        """Remove all ANSI color/format codes from the output."""
        output = output.strip()
        output = output.replace("\x1b[31m", "")    # Red
        output = output.replace("\x1b[32m", "")    # Green
        output = output.replace("\x1b[33m", "")    # Yellow
        output = output.replace("\x1b[1;33m", "")  # Bold Yellow
        output = output.replace("\x1b[m", "")      # Reset
        output = output.replace("\x1b[0m", "")     # Reset
        return output

    def tree(self):
        output = self.run('tree')
        return output.replace("\n.\n", f"\n{self.path}:\n")

    def write_file(self, filename, content):
        with open(os.path.join(self.path, filename), 'w') as f:
            f.write(content)

    def cat_file_one(self):
        result = self.run("cat file-1.txt")
        return result

    def cat_file_two(self):
        result = self.run("cat file-2.txt")
        return result

    def stage_file_one(self):
        self.run("git add file-1.txt")

    def stage_file_two(self):
        self.run("git add file-2.txt")

    def stage_both_files(self):
        self.stage_file_one()
        self.stage_file_two()

    def setup_initial_commit(self):
        self.write_file('file-1.txt', 'Initial change for file one.\n')
        self.write_file('file-2.txt', 'Initial change for file two.\n')
        self.stage_both_files()
        self.run("git commit -m 'Initial committed change'")

    def setup_first_changes(self):
        self.write_file('file-1.txt', 'First revision for file one.\n')
        self.write_file('file-2.txt', 'First revision for file two.\n')

    def setup_first_stash(self):
        self.setup_first_changes()
        self.run("git stash push -m 'First Stash'")

    def setup_first_commit(self, message=None):
        self.setup_first_changes()
        self.stage_both_files()
        message = message or 'First committed change'
        self.run(f'git commit -m "{message}"')

    def setup_second_changes(self):
        self.write_file('file-1.txt', 'Second revision for file one.\n')
        self.write_file('file-2.txt', 'Second revision for file two.\n')

    def setup_second_stash(self):
        self.setup_second_changes()
        self.run("git stash push -m 'Second Stash'")

    def setup_second_commit(self, message=None):
        self.setup_second_changes()
        self.stage_both_files()
        message = message or 'Second committed change'
        self.run(f'git commit -m "{message}"')

    def setup_third_changes(self):
        self.write_file('file-1.txt', 'Third revision for file one.\n')
        self.write_file('file-2.txt', 'Third revision for file two.\n')

    def setup_third_stash(self):
        self.setup_third_changes()
        self.run("git stash push -m 'Third Stash'")

    def setup_third_commit(self, message=None):
        self.setup_third_changes()
        self.stage_both_files()
        message = message or 'Third committed change'
        self.run(f'git commit -m "{message}"')


if __name__ == "__main__":
    os.system('clear')
    repo = RepositoryFixture('repo-test')
    repo.setup_first_commit()
    repo.setup_second_commit()
    repo.print("git state") # clean repo
    repo.setup_third_changes()
    print(repo.tree())
    repo.print("git state") # uncommitted changes
    repo.teardown()
