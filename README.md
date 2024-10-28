# Git Aliases

## Undo Local Commit

Undo the last local commit while preserving changes in the working directory without the difficult to remember `git reset --soft HEAD~1`.

```bash
git config --global alias.uncommit '!git log -1 --oneline --color=always | sed "s/^/Uncommitted: /" && git reset --soft HEAD~1'
```

```bash
$ git uncommit
Uncommitted: e4ac8e05a add user authentication endpoint
```

## Feature Branch Management

Create a new feature branch from the current branch with a random identifier. Note that it relies on dashes as a delimiter, so it can't be used if your branch names include dashes.

```bash
git config --global alias.feature '!git checkout -b feature-$(git branch --show-current)-$(openssl rand -hex 4) $(git branch --show-current)'
```

```bash
$ git feature
M src/components/Navbar.jsx
Switched to a new branch 'feature-dev-0dc6a7a1'
```

## Refresh & Clean Branches

This is intended to be used after the feature branch has been merged. This command will temporarily stash changes (if any), switch back to the original branch, pull the latest changes, delete any local branches prefixed with "feature-", and reapply the temporarily stashed changes.

```bash
git config --global alias.refresh '!branch=$(git branch --show-current); original_branch=$(echo $branch | cut -d"-" -f2); git stash && git checkout $original_branch && git pull && git branch | grep "feature-" | xargs git branch -D && git stash pop && git branch'
```

```bash
$ git refresh
Saved working directory and index state WIP on feature-dev-0dc6a7a1:
...
Switched to branch 'dev'
...
Deleted branch feature-dev-0dc6a7a1 (was a8ff0a5c6).
...
Your branch is up to date with 'origin/dev'.
...
Dropped refs/stash@{0} (3a116bd1a3eca73c79ea0bcba2004f85fcb1a68c)
```

## View Recent Commit History

View recent commits in a clean, terminal-width-aware format.

- Shows last 20 commits
- Truncates to avoid wrapping based on terminal width
- Adds ellipsis for truncated lines

```bash
git config --global alias.last '!cols=$(tput cols); color_padding=11; git log -n 20 --oneline --color=always | while read -r line; do if [ ${#line} -gt $((cols-3)) ]; then echo "${line:0:$((cols+color_padding-6))}..."; else echo "$line"; fi; done'
```

```bash
$ git last
d4e5f67 PROJ-1234 - Implement new authentication flow with OAuth2 and add support for multipl...
b3c4d56 PROJ-1233 - Fix edge case in user session handling
a2b3c45 PROJ-1232 - Update service worker implementation to handle offline mode and cache inv...
9a8b7c6 PROJ-1231 - Refactor database migration scripts for better performance and add new in...
8f7e6d5 PROJ-1230 - Add comprehensive integration tests for payment processing workflow
7d6e5f4 PROJ-1229 - Update API documentation with new authentication endpoints
6c5d4e3 PROJ-1228 - Fix race condition in concurrent user profile updates
5b4c3d2 PROJ-1227 - Implement real-time notification system with WebSocket integration and re...
4a3b2c1 PROJ-1226 - Add support for multi-factor authentication
3f2e1d0 PROJ-1225 - Optimize image processing pipeline and implement lazy loading strategy fo...
...
```

## Hide/Unhide Changes

Send unstaged changes to a stash named "hidden". Add more uncommitted changes if needed, and easily reapply them later.

```bash
git config --global alias.hidden '!git stash list | grep ": hidden" | head -n1 | cut -d: -f1 | xargs -I {} git show --pretty="" --name-only {} | while read file; do echo "  Hidden: \033[31m$file\033[0m"; done'

git config --global alias.hide '!git unhide > /dev/null 2>&1 || true && git stash push --keep-index -m "hidden" > /dev/null && git hidden'

git config --global alias.unhide '!f() { files=$(git hidden | sed "s/  Hidden:/  Unhidden:/g" | sed "s/\x1b\[31m/\x1b\[32m/g"); git stash list | grep "hidden" | head -n1 | cut -d: -f1 | xargs -I {} git stash pop {} > /dev/null 2>&1; echo "$files"; }; f'
```

```bash
# Stash the unstaged changes
$ git hide
  Hidden: src/components/Feature.jsx
  Hidden: src/components/Header.jsx

# Restore the hidden changes
$ git unhide
  Unhidden: src/components/Feature.jsx
  Unhidden: src/components/Header.jsx
```
