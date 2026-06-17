# Lab: Working with `git worktree`

Creating a hands-on lab that teaches `git worktree` — a powerful Git feature that lets you check out **multiple branches at the same time** in **separate directories**, all sharing a single repository and history. This is ideal for working on a feature while handling an urgent hotfix, running long builds/tests on one branch while coding on another, or reviewing a pull request without stashing your current work.

### Objective
To gain practical experience with `git worktree add`, `git worktree list`, `git worktree remove`, and `git worktree prune`, and to understand when worktrees are better than the classic *stash / switch branch / switch back* workflow.

### Why use worktrees instead of `git stash` + `git checkout`?
- **No context switching cost** — your feature branch stays exactly as it is in its own folder; nothing to stash or unstash.
- **True parallelism** — build/test branch A in one terminal while you edit branch B in another.
- **One shared repo** — all worktrees share the same `.git` object database, so there is no duplicate clone and no wasted disk space.
- **Safer hotfixes** — fix `main` in a clean worktree without disturbing your half-finished feature.

### Prerequisites
- Git **2.5 or newer** (worktrees were added in 2.5; `worktree remove` needs 2.17+). Check with:
  ```bash
  git --version
  ```
- Basic knowledge of `git init`, `git add`, `git commit`, `git branch`, and `git log`.
- A terminal (bash, zsh, Git Bash, or WSL).

---

## Part 1: Create the Main Repository

#### Task 1: Initialize a project and make a first commit
```bash
# Create and enter a working folder for this lab
mkdir worktree-lab
cd worktree-lab

# Create the "main" repository (this is the primary worktree)
mkdir main-repo
cd main-repo
git init
git branch -M main

# Create an initial file and commit it
echo "# Awesome App" > README.md
echo "console.log('v1');" > app.js
git add .
git commit -m "Initial commit: app v1"

# Confirm the starting state
git log --oneline
git status
```

You now have a normal repository. The folder `main-repo` is your **primary worktree** and it is checked out on the `main` branch.

---

## Part 2: Add a Worktree for a New Feature

#### Task 2: Create a linked worktree on a brand-new branch
The `-b` flag creates a new branch **and** checks it out into a new folder in a single step.

```bash
# Run this from inside main-repo
# Syntax: git worktree add -b <new-branch> <path> <start-point>
git worktree add -b feature-login ../feature-login main
```

Read the output carefully — Git reports that it created a new worktree and a new branch `feature-login`.

#### Task 3: Inspect all worktrees
```bash
git worktree list
```
Expected output (paths and hashes will differ):
```
/path/to/worktree-lab/main-repo        a1b2c3d [main]
/path/to/worktree-lab/feature-login    a1b2c3d [feature-login]
```
Notice that **both** worktrees point at the same commit for now, but they are on **different branches**.

#### Task 4: Do real work in the feature worktree
```bash
cd ../feature-login

# Make a change that only exists on this branch
echo "function login() { return 'ok'; }" > login.js
git add login.js
git commit -m "Add login feature"

git log --oneline
```

---

## Part 3: Handle an Urgent Hotfix in Parallel

This is the scenario worktrees were built for: your feature is **half-finished**, and a bug on `main` needs an immediate fix — with **no stashing**.

#### Task 5: Leave the feature in a messy, uncommitted state
```bash
# Still inside feature-login — start more work but DON'T commit it
echo "// TODO: still working on this" >> login.js
git status        # shows login.js as modified / not staged
```

#### Task 6: Spin up a clean hotfix worktree from `main`
```bash
# Add a worktree for an existing-or-new hotfix branch off main
git worktree add -b hotfix-typo ../hotfix-typo main

cd ../hotfix-typo
# main is clean here — fix the bug
echo "console.log('v1 - fixed typo');" > app.js
git add app.js
git commit -m "Hotfix: correct log message"
git log --oneline
```

#### Task 7: Merge the hotfix into `main` and confirm the feature was untouched
```bash
# Move to the main worktree and merge the hotfix
cd ../main-repo
git merge hotfix-typo
git log --oneline

# Now return to the feature worktree — your uncommitted work is exactly as you left it
cd ../feature-login
git status        # login.js is STILL modified — nothing was lost or stashed
```
**Key takeaway:** you fixed `main` and merged it *without ever disturbing* your in-progress feature.

---

## Part 4: Add a Worktree from an Existing Branch

You can also create a worktree for a branch that already exists (e.g. to review a colleague's branch).

#### Task 8: Create a branch, then check it out in its own worktree
```bash
cd ../main-repo
git branch experiment            # create a branch but stay on main
git worktree add ../experiment experiment   # check it out into its own folder
git worktree list
```
> ⚠️ **Rule to remember:** a branch can be checked out in **only one worktree at a time**. Try `git worktree add ../dup main` and Git will refuse, because `main` is already checked out in `main-repo`. This protection prevents two folders from fighting over the same branch.

---

## Part 5: Clean Up Worktrees

#### Task 9: Remove a worktree you are finished with
```bash
cd ../main-repo

# Remove the hotfix worktree folder cleanly (deletes the directory)
git worktree remove ../hotfix-typo
git worktree list      # hotfix-typo is gone

# The branch still exists in the repo; delete it too if it was merged and no longer needed
git branch -d hotfix-typo
```

#### Task 10: Handle a manually-deleted worktree with `prune`
```bash
# Simulate deleting a worktree folder by hand (NOT the recommended way)
rm -rf ../experiment

# Git still has stale bookkeeping for it
git worktree list      # experiment shows as "prunable" / missing

# Clean up the stale administrative files
git worktree prune
git worktree list      # the stale entry is now removed
```
> 💡 Prefer `git worktree remove` over `rm -rf`. Use `git worktree prune` only to clean up after a folder was deleted manually or lost (e.g. an external drive was unplugged).

---

## Quick Command Reference

| Command | What it does |
| --- | --- |
| `git worktree add <path> <branch>` | Check out an existing branch into a new folder |
| `git worktree add -b <new-branch> <path> [start]` | Create a new branch and a worktree for it |
| `git worktree add --detach <path>` | Create a worktree in detached HEAD (no branch) |
| `git worktree list` | Show all worktrees and the branch each has checked out |
| `git worktree remove <path>` | Cleanly remove a worktree (must be clean unless `--force`) |
| `git worktree move <path> <new-path>` | Relocate a worktree |
| `git worktree prune` | Delete bookkeeping for worktrees whose folders are gone |
| `git worktree lock <path>` | Prevent a worktree from being pruned (e.g. on removable media) |

---

## Deliverables
1. **Step-by-Step Report** — document each task with the command used and its output (screenshots welcome), especially:
   - The output of `git worktree list` after Part 2 and after Part 5.
   - Proof in Task 7 that the feature worktree kept its uncommitted change after the hotfix.
2. **Reflective Summary** — in a few sentences, explain a real situation from your own projects where you would reach for `git worktree` instead of `git stash`.

## Assessment Criteria
- Correctly created, listed, and removed worktrees.
- Demonstrated the parallel hotfix workflow without losing in-progress work.
- Showed understanding of the *"one branch, one worktree"* rule and the difference between `remove` and `prune`.
- Clarity and completeness of the report and reflection.

## Challenge (Optional)
- Open each worktree in a separate terminal tab and run a long command (e.g. `sleep 30 && echo done`) on the feature branch while committing on `main` — observe true parallel work.
- From the `main-repo`, run `git log --oneline --all --graph` and identify the commits that belong to each worktree's branch.
