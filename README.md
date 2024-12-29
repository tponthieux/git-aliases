# Git Alias Commands

A collection of Git aliases that add helpful commands, and simplify common workflows.


To install these aliases, either run the respective commands individually, or execute the test script:

```bash
python3 src/test.py
```


To remove the aliases, you can use these commands:

```bash
# Remove a specific alias
git config --global --unset alias.feature
git config --global --unset alias.refresh
git config --global --unset alias.hide
git config --global --unset alias.hidden
git config --global --unset alias.unhide
git config --global --unset alias.pluck
git config --global --unset alias.last
git config --global --unset alias.uncommit
git config --global --unset alias.state
git config --global --unset alias.aliases

# Remove all aliases
git config --global --remove-section alias
```

## Git Feature

Create a new feature branch from the current branch with a random identifier. Note that it relies on dashes as a delimiter, so it can't be used if your branch names include dashes.

```bash
git config --global alias.feature '!git state && git checkout -b feature-$(git branch --show-current)-$(openssl rand -hex 4) 2>&1'
```

```console
$ git branch
* dev

$ git feature
Branch: dev

Unstaged:
 M file-1.txt    modified file

Staged:
M  file-2.txt    modified file
Switched to a new branch 'feature-dev-4d1fc795'

$ git branch
  dev
* feature-dev-4d1fc795
```

## Git Refresh

This is intended to be used after the feature branch generated via the 'git feature' alias has been merged on the remote repository. This command will temporarily stash changes (if any), switch back to the original branch, pull the latest changes, delete any local branches prefixed with "feature-", and reapply the temporarily stashed changes.

```bash
git config --global alias.refresh '!branch=$(git branch --show-current); original_branch=$(echo $branch | cut -d"-" -f2); git stash && git checkout $original_branch && git pull && git branch | grep "feature-" | xargs git branch -D && git stash pop && git branch'
```

```console
$ git branch
  dev
* feature-dev-0dc6a7a1

$ git refresh
Saved working directory and index state WIP on feature-dev-0dc6a7a1: 3e0da65 Second committed change
Your branch is up to date with 'origin/dev'.
Updating f666c3e..3e0da65
Fast-forward
 file-1.txt | 2 +-
 file-2.txt | 2 +-
 2 files changed, 2 insertions(+), 2 deletions(-)
Deleted branch feature-dev-0dc6a7a1 (was 3e0da65).
On branch dev
Your branch is up to date with 'origin/dev'.

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
  modified:   file-1.txt
  modified:   file-2.txt

no changes added to commit (use "git add" and/or "git commit -a")
Dropped refs/stash@{0} (04d66abf6b1fb96e10b5e6635c3bdbc48f60ed04)
* dev
```

## Git Hide

Send unstaged changes to a stash named "hidden". You can add more uncommitted changes to the same stash if needed with the same command.

```bash
git config --global alias.hide '!git unhide > /dev/null 2>&1 || true && git stash push --keep-index -m "hidden" > /dev/null && git hidden'
```

```console
$ git state
Branch: dev

Unstaged:
 M file-1.txt    modified file

Staged:
M  file-2.txt    modified file

$ git hide
  Hidden: file-1.txt

$ git stash list
stash@{0}: On dev: hidden

$ git state
Branch: dev

Unstaged:
 M file-1.txt    modified file

Staged:
M  file-2.txt    modified file

$ git hide
  Hidden: file-1.txt

$ git stash list
stash@{0}: On dev: hidden
stash@{1}: On dev: hidden

$ git unhide
  Unhidden: file-1.txt

$ git stash list
stash@{0}: On dev: hidden
```

## Git Hidden

List the file names for changes stored in a stash named "hidden".

```bash
git config --global alias.hidden '!git stash list | grep ": hidden" | head -n1 | cut -d: -f1 | xargs -I {} git show --pretty="" --name-only {} | while read file; do echo "  Hidden: \033[31m$file\033[0m"; done'
```

```console
$ git state
Branch: dev

Unstaged:
 M file-1.txt    modified file
 M file-2.txt    modified file

$ git add file-2.txt

$ git state
Branch: dev

Unstaged:
 M file-1.txt    modified file

Staged:
M  file-2.txt    modified file

$ git hide
  Hidden: file-1.txt

$ git state
Branch: dev

Staged:
M  file-2.txt    modified file

$ git stash list
stash@{0}: On dev: hidden

$ git hidden
  Hidden: file-1.txt
```

## Git Unhide

Restore the hidden changes from the stash named "hidden".
*Not currently working when there is a conflict.*

```bash
git config --global alias.unhide '!f() { files=$(git hidden | sed "s/  Hidden:/  Unhidden:/g" | sed "s/\x1b\[31m/\x1b\[32m/g"); git stash list | grep "hidden" | head -n1 | cut -d: -f1 | xargs -I {} git stash pop {} > /dev/null 2>&1; echo "$files"; }; f'
```

```console
$ git state
Branch: dev

Unstaged:
 M file-1.txt    modified file

Staged:
M  file-2.txt    modified file

$ git hide
  Hidden: file-1.txt

$ git stash list
stash@{0}: On dev: hidden

$ git state
Branch: dev

Staged:
M  file-2.txt    modified file

$ git unhide
  Unhidden: file-1.txt

$ git state
Branch: dev

Unstaged:
 M file-1.txt    modified file

Staged:
M  file-2.txt    modified file
```

## Git Pluck

Pop a specific stash by index and display the remaining stashes. Without an index argument, it will list the available stashes.

```bash
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
```

```console
$ git pluck
Available stashes:
stash@{0}: On dev: Third Stash
stash@{1}: On dev: Second Stash
stash@{2}: On dev: First Stash

Usage: git pluck <index>

$ git pluck 1
Plucking: stash@{1}: On dev: Second Stash

Remaining stashes:
stash@{0}: On dev: Third Stash
stash@{1}: On dev: First Stash

$ git pluck 0
Plucking: stash@{0}: On dev: Third Stash

error: Your local changes to the following files would be overwritten by merge:
  file-1.txt
  file-2.txt

Please commit your changes or stash them before you merge.

Remaining stashes:
stash@{0}: On dev: Third Stash
stash@{1}: On dev: First Stash
```

## Git Last

View recent commits in a clean, terminal-width-aware format.
    - Shows the last 20 commits
    - Truncates to avoid wrapping based on terminal width
    - Adds ellipsis for truncated lines

```bash
git config --global alias.last '!cols=$(tput cols); color_padding=11; git log -n 20 --oneline --color=always | while read -r line; do if [ ${#line} -gt $((cols-3)) ]; then echo "${line:0:$((cols+color_padding-6))}..."; else echo "$line"; fi; done'
```

```console
$ git last
234340e Third committed change. Truncated to fit the terminal width...
410f85d Second committed change
2ad18a1 First committed change
```

## Git Uncommit

Undo the last local commit while preserving changes in the working directory without the difficult to remember `git reset --soft HEAD~1`.

```bash
git config --global alias.uncommit '!git log -1 --oneline --color=always | sed "s/^/Uncommitted: /" && git reset --soft HEAD~1'
```

```console
$ git log --oneline
ff49eff Third committed change
410f85d Second committed change
2ad18a1 First committed change

$ git uncommit
Uncommitted: ff49eff Third committed change
```

## Git State

Show the current state of the working directory and staging area.

```bash
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
```

```console
$ git state
Branch: dev

Unstaged:
 D file-1.txt         deleted file
?? subdir/file.txt    untracked file

Staged:
M  file-1.txt         unrecognized status code
M  file-2.txt         modified file
```

## Git Aliases

List all of the available Git aliases.

```bash
git config --global alias.aliases '!printf "Available Commands:\n" && git config --get-regexp alias | grep "^alias\." | awk -F"[. ]" "{print \"  git \" \$2}"'
```

```console
$ git aliases
Available Commands:
  git feature
  git state
  git refresh
  git hide
  git hidden
  git unhide
  git pluck
  git last
  git uncommit
  git aliases
```
