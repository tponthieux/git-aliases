import os
import importlib
import subprocess
from pathlib import Path


class TestRunner:
    """Removes and recreates the known aliases, and runs the unit tests."""

    def __init__(self):
        self.alias_names = []
        self.get_alias_modules()
        self.remove_aliases()

    def get_alias_modules(self):
        """Load and store the alias modules from the Aliases directory."""

        self.src_path = Path(os.path.join(Path(__file__).parent, 'Aliases'))
        self.alias_modules = []

        for file in sorted(self.src_path.glob('*.py'), key=lambda f: f.name):
            module_name = f'Aliases.{file.stem}'
            module = importlib.import_module(module_name)
            self.alias_modules.append(module)
            print(module_name)

    def remove_aliases(self):
        """Removes the known aliases from the global Git configuration."""

        for module in self.alias_modules:
            alias_name = module.command().split('alias.')[1].split("'")[0].strip()
            self.alias_names.append(alias_name)

            # If the alias exists (return code 0), remove it
            result = subprocess.run(['git', 'config', '--global', '--get', f'alias.{alias_name}'], capture_output=True, text=True)
            if result.returncode == 0:
                subprocess.run(['git', 'config', '--global', '--unset', f'alias.{alias_name}'], check=True)
                print(f"Removed alias: {alias_name}")

    def run_tests(self):
        """Execute unit tests for all the loaded alias modules."""

        for module in self.alias_modules:
            module.test() # Make sure the unit test passes


if __name__ == '__main__':
    os.system('clear')
    test_runner = TestRunner()
    test_runner.run_tests()
