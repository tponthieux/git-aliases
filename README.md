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
git config --global --unset alias.aliases

# Remove all aliases
git config --global --remove-section alias
```

## Git Feature

Create a new feature branch from the current branch with a random identifier. Note that it relies on dashes as a delimiter, so it can't be used if your branch names include dashes.

```bash
git config --global alias.feature '!git status --short && git checkout -b feature-$(git branch --show-current)-$(openssl rand -hex 4) 2>&1'
```

```console
$ git branch
* dev

$ git feature
 M file-1.txt
M  file-2.txt
Switched to a new branch 'feature-dev-01b79a67'

$ git branch
  dev
* feature-dev-01b79a67
```

## Git Refresh

This is intended to be used after the feature branch generated via the 'git feature' alias has been merged on the remote repository. This command will temporarily stash changes (if any), switch back to the original branch, pull the latest changes, delete any local branches prefixed with "feature-", and reapply the temporarily stashed changes.

```bash
git config --global alias.refresh '!branch=$(git branch --show-current); original_branch=$(echo $branch | cut -d"-" -f2); git stash && git checkout $original_branch && git pull && git branch | grep "feature-" | xargs git branch -D && git stash pop && git branch'
```

```console
$ git refresh
Saved working directory and index state WIP on feature-dev-0dc6a7a1: 5d530cd Second committed change
Your branch is up to date with 'origin/dev'.
Updating 3e9a9af..5d530cd
Fast-forward
 file-1.txt | 2 +-
 file-2.txt | 2 +-
 2 files changed, 2 insertions(+), 2 deletions(-)
Deleted branch feature-dev-0dc6a7a1 (was 5d530cd).
On branch dev
Your branch is up to date with 'origin/dev'.

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
  modified:   file-1.txt
  modified:   file-2.txt

no changes added to commit (use "git add" and/or "git commit -a")
Dropped refs/stash@{0} (c42c9ad3121068b258f4c6194af3eb060279a9d5)
* dev
```

## Git Hide

Send unstaged changes to a stash named "hidden". You can add more uncommitted changes to the same stash if needed with the same command.

```bash
git config --global alias.hide '!git unhide > /dev/null 2>&1 || true && git stash push --keep-index -m "hidden" > /dev/null && git hidden'
```

```console
$ git status --porcelain
 M file-1.txt     # unstaged: modified file
M  file-2.txt     # staged: modified file

$ git hide
  Hidden: file-1.txt

$ git stash list
stash@{0}: On dev: hidden

$ git status --short
 M file-1.txt
M  file-2.txt

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
$ git status --porcelain
 M file-1.txt
 M file-2.txt

$ git add file-2.txt

$ git status --porcelain
 M file-1.txt
M  file-2.txt

$ git hide
  Hidden: file-1.txt

$ git status --porcelain
M  file-2.txt

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
$ git status --porcelain
 M file-1.txt     # unstaged: modified file
M  file-2.txt     # staged: modified file

$ git hide
  Hidden: file-1.txt

$ git stash list
stash@{0}: On dev: hidden

$ git status --porcelain
M  file-2.txt     # staged: modified file

$ git unhide
  Unhidden: file-1.txt

$ git status --porcelain
 M file-1.txt     # unstaged: modified file
M  file-2.txt     # staged: modified file
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
2cec8e7 Third committed change. Truncated to fit the terminal width...
7b2009d Second committed change
9ce46be First committed change
```

## Git Uncommit

Undo the last local commit while preserving changes in the working directory without the difficult to remember `git reset --soft HEAD~1`.

```bash
git config --global alias.uncommit '!git log -1 --oneline --color=always | sed "s/^/Uncommitted: /" && git reset --soft HEAD~1'
```

```console
$ git log --oneline
b9c08a8 Third committed change
7b2009d Second committed change
9ce46be First committed change

$ git uncommit
Uncommitted: b9c08a8 Third committed change
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
  git refresh
  git hide
  git hidden
  git unhide
  git pluck
  git last
  git uncommit
  git aliases
```
