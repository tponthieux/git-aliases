import os
import sys
from pathlib import Path

# Local imports
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.Lib.fixture import RepositoryFixture
from src.Lib.verifier import Verify

def heading():
    return 'Git State'

def description():
    return 'Show the current state of the working directory and staging area.'

def command():
    return r'''
    git config --global alias.state '!f() {
      lf="
"
      get_properties() {
        case "$1" in
          "##") echo "Heading|" ;;
          " M") echo "Unstaged|modified file" ;;
          " D") echo "Unstaged|deleted file" ;;
          "??") echo "Unstaged|untracked file" ;;
          "MM") echo "Mixed|staged modifications plus unstaged modifications" ;;
          "AM") echo "Mixed|staged new file plus unstaged modifications" ;;
          "MD") echo "Mixed|staged modifications plus unstaged deletion" ;;
          "AD") echo "Mixed|staged new file plus unstaged deletion" ;;
          "RD") echo "Mixed|staged rename plus unstaged deletion" ;;
          "RM") echo "Mixed|staged rename plus unstaged modifications" ;;
          "CM") echo "Mixed|staged copy plus unstaged modifications" ;;
          "CD") echo "Mixed|staged copy plus unstaged deletion" ;;
          "A ") echo "Staged|added new file" ;;
          "M ") echo "Staged|modified file" ;;
          "D ") echo "Staged|deleted file" ;;
          "R ") echo "Staged|renamed file" ;;
          "C ") echo "Staged|copied file" ;;
          "UU") echo "Conflicted|both modified" ;;
          "DD") echo "Conflicted|both deleted" ;;
          "AA") echo "Conflicted|both added" ;;
          "AU") echo "Conflicted|our new file conflicts with their path" ;;
          "UA") echo "Conflicted|their new file conflicts with our path" ;;
          "DU") echo "Conflicted|deleted by us, modified by them" ;;
          "UD") echo "Conflicted|modified by us, deleted by them" ;;
          *) echo "Uncategorized|unrecognized status code" ;;
        esac
      }

      yellow() {
        local BOLD_YELLOW="\033[1;33m"
        local NO_COLOR="\033[0m"
        printf "${BOLD_YELLOW}$1${NO_COLOR}"
      }

      status_lines=$(git status --short --branch --untracked-files=all)
      max_length=$(echo "$status_lines" | wc -L)

      heading_lines=""
      unstaged_lines=""
      conflict_lines=""
      staged_lines=""
      uncategorized_lines=""

      IFS="$lf" read -r -d "" -a status_lines <<< "$status_lines"

      for line in "${status_lines[@]}"; do
        code=${line:0:2}
        rest=${line:2}
        properties=$(get_properties "$code")
        category=$(echo "$properties" | cut -d"|"  -f1)
        padding=$(printf "%*s    " $((max_length - ${#line})) "")
        description=$(yellow "$(echo "$properties" | cut -d"|" -f2)")

        if [ "$category" == "Heading" ]; then
          heading_lines+="$(yellow "Branch:")${rest}${lf}"
        fi

        if [ "$category" == "Unstaged" ]; then
          unstaged_lines+="$(yellow "${code}")${rest}${padding}${description}${lf}"
        fi

        if [ "$category" == "Mixed" ]; then
          # keep second character, replace first with space
          unstaged_code=" ${code:1}"
          unstaged_properties=$(get_properties "$unstaged_code")
          unstaged_description=$(yellow "$(echo "$unstaged_properties" | cut -d"|" -f2)")
          unstaged_lines+="$(yellow "${unstaged_code}")${rest}${padding}${unstaged_description}${lf}"

          # keep first character, replace second with space
          staged_code="${code:0:1}"
          staged_properties=$(get_properties "$staged_code")
          staged_description=$(yellow "$(echo "$staged_properties" | cut -d"|" -f2)")
          staged_lines+="$(yellow "${staged_code} ")${rest}${padding}${staged_description}${lf}"
        fi

        if [ "$category" == "Staged" ]; then
          staged_lines+="$(yellow "${code}")${rest}${padding}${description}${lf}"
        fi

        if [ "$category" == "Conflicted" ]; then
          conflict_lines+="$(yellow "${code}")${rest}${padding}${description}${lf}"
        fi

        if [ "$category" == "Uncategorized" ]; then
          uncategorized_lines+="$(yellow "${code}")${rest}${padding}${description}${lf}"
        fi
      done

      output=""

      if [ "$heading_lines" ]; then
        output+="${heading_lines}"
      fi

      if [ "$conflict_lines" ]; then
        output+="${lf}$(yellow "Conflicts:")"
        output+="${lf}${conflict_lines}"
      fi

      if [ "$unstaged_lines" ]; then
        output+="${lf}$(yellow "Unstaged:")"
        output+="${lf}${unstaged_lines}"
      fi

      if [ "$staged_lines" ]; then
        output+="${lf}$(yellow "Staged:")"
        output+="${lf}${staged_lines}"
      fi

      if [ "$uncategorized_lines" ]; then
        output+="${lf}$(yellow "Uncategorized:")"
        output+="${lf}${uncategorized_lines}"
      fi

      # Trim trailing whitespace
      # echo "${output%"${output##*[![:space:]]}"}"
      # printf "%s" "$output" | awk "{print \$0}"
      printf "%s" "$output"
    }; f'
    '''.strip()

def example():
    """Get a console output example for the alias."""
    # Setup the repository
    repo = RepositoryFixture('state-test')
    repo.run(command())
    repo.setup_initial_commit()
    repo.setup_first_changes()
    repo.stage_file_one()
    repo.stage_file_two()
    repo.run('rm file-1.txt')
    repo.run('mkdir subdir')
    repo.run('touch subdir/file.txt')

    # Get the console output
    output = repo.run("git state")

    repo.teardown()
    return repo.clean(output)

def test():
    """Test the Git state alias."""
    # Setup
    repo = RepositoryFixture('state-test')
    repo.run(command())
    repo.run('mkdir subdir')
    repo.run('touch subdir/file.txt')

    # Nothing is staged
    repo.setup_first_changes()
    output = repo.print("git state")
    Verify(output).contains("?? file-1.txt")
    Verify(output).contains("?? file-2.txt")
    Verify(output).contains("?? subdir/file.txt")

    # Has staged and unstaged changes
    repo.stage_file_two()
    output = repo.print("git state")
    Verify(output).contains("A file-2.txt")
    Verify(output).contains("?? file-1.txt")
    Verify(output).contains("?? subdir/file.txt")

    # Has only staged changes
    repo.stage_file_one()
    output = repo.print("git state")
    Verify(output).contains("A file-1.txt")
    Verify(output).contains("A file-2.txt")
    Verify(output).contains("?? subdir/file.txt")

    repo.teardown()

if __name__ == '__main__':
    os.system('clear')

    print('#### Running example() ####\n')
    print(example())

    # print('\n#### Running test() ####\n')
    # test()