import os
import sys
from pathlib import Path

# Local imports
from test import TestRunner
sys.path.append(str(Path(__file__).parent.parent))


class ReadmeGenerator:
    """Generate the README.md file from the alias modules."""

    def __init__(self, file_path):
        """Initialize the Readme Generator."""
        self.test_runner = TestRunner()
        self.readme_path = file_path
        self.initialize_new_readme()
        self.generate_readme()
        self.replace_hard_tabs()

    def initialize_new_readme(self):
        """Initialize a new README file."""
        with open(self.readme_path, 'w') as f:
            f.write('')

    def generate_readme(self):
        """Generate the README file."""

        content_lines = [
            '# Git Alias Commands\n',
            'A collection of Git aliases that add helpful commands, and simplify common workflows.\n',
        ]

        content_lines.extend([
            '\nTo install these aliases, either run the respective commands individually, or execute the test script:\n',
            '```bash',
            'python3 src/test.py',
            '```\n'
        ])

        content_lines.extend([
            '\nTo remove the aliases, you can use these commands:\n',
            '```bash',
            '# Remove a specific alias'
        ])

        # Add unset command for each alias
        for alias_name in self.test_runner.alias_names:
            content_lines.append(f'git config --global --unset alias.{alias_name}')

        content_lines.extend([
            '',
            '# Remove all aliases',
            'git config --global --remove-section alias',
            '```\n'
        ])

        for module in self.test_runner.alias_modules:
            module.test() # Make sure the unit test passes
            heading = module.heading()
            description = module.description()
            command = module.command()
            console = module.example()

            content_lines.extend([
              f'## {heading}\n',
              f'{description}\n',
              f'```bash\n{command}\n```\n',
              f'```console\n{console}\n```\n'
            ])

        content = '\n'.join(content_lines)

        with open(self.readme_path, 'w') as f:
            f.write(content)

        print(content)

    def replace_hard_tabs(self):
        """Replace hard tabs with spaces."""
        with open(self.readme_path, 'r') as f:
            content = f.read()

        content = content.replace('\t', '  ')

        with open(self.readme_path, 'w') as f:
            f.write(content)


if __name__ == '__main__':
    os.system('clear')
    ReadmeGenerator('README.md')
