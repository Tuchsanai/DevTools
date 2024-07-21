## Git Lab Exercise: Resolving Merge Conflicts

### Objective
Learn how to resolve a merge conflict in Git that occurs when changes in two branches are incompatible.

### Setup

1. Open the terminal.
2. Navigate to a suitable directory for your project.

3. **Create a new directory for the repository:**
   ```bash
   mkdir mygit-lab3
   cd mygit-lab3
   ```

4. Initialize a new Git repository:
   ```bash
   git init
   ```

### Task 1: Create Initial Commit in `master` Branch

1. Create a file `conflict.txt` and make the initial commit:
   ```bash
   echo "Line 1: This is the start of the document." > conflict.txt
   git add conflict.txt
   git commit -m "Initial commit on master"
   ```

### Explanation:
- `echo "Line 1: This is the start of the document." > conflict.txt`: Creates a new file named `conflict.txt` with the content "Line 1: This is the start of the document."
- `git add conflict.txt`: Stages the new file for commit.
- `git commit -m "Initial commit on master"`: Commits the staged file with the message "Initial commit on master."

### Task 2: Add More Commits to `master` Branch

1. Add a new line to `conflict.txt` and commit:
   ```bash
   echo "Line 2: Additional line in master branch." >> conflict.txt
   git add conflict.txt
   git commit -m "Second commit on master"
   ```

2. Make another change and commit:
   ```bash
   echo "Line 3: Further changes in master branch." >> conflict.txt
   git add conflict.txt
   git commit -m "Third commit on master"
   ```

3. Display the file content:
   ```bash
   cat conflict.txt
   ```

4. Check the commit history:
   ```bash
   git log --oneline
   ```

### Explanation:
- `echo "Line 2: Additional line in master branch." >> conflict.txt`: Appends the line to the existing `conflict.txt`.
- `git add conflict.txt`: Stages the updated file for commit.
- `git commit -m "Second commit on master"`: Commits the staged changes with the message "Second commit on master."
- `cat conflict.txt`: Displays the current content of the file.
- `git log --oneline`: Shows a simplified commit history.

### Task 3: Create `new_branch` and Add Commits

1. Create a new branch named `new_branch` and switch to it:
   ```bash
   git checkout -b new_branch
   ```

2. Make changes to `conflict.txt` that will conflict with `master`:
   ```bash
   echo "Line 1 (new branch): This line will cause a merge conflict." > conflict.txt
   git add conflict.txt
   git commit -m "First commit on new_branch"
   ```

3. Add another conflicting line and commit:
   ```bash
   echo "Line 2 (new branch): This is another conflicting line." >> conflict.txt
   git add conflict.txt
   git commit -m "Second commit on new_branch"
   ```

### Explanation:
- `git checkout -b new_branch`: Creates and switches to a new branch named `new_branch`.
- `echo "Line 1 (new branch): This line will cause a merge conflict." > conflict.txt`: Replaces the content of `conflict.txt` in `new_branch` with a conflicting line.
- `git add conflict.txt`: Stages the new content for commit.
- `git commit -m "First commit on new_branch"`: Commits the staged changes with the message "First commit on new_branch."
- `echo "Line 2 (new branch): This is another conflicting line." >> conflict.txt`: Appends another conflicting line.
- `git add conflict.txt`: Stages the updated file for commit.
- `git commit -m "Second commit on new_branch"`: Commits the staged changes with the message "Second commit on new_branch."

### Task 4: Add New Commit in `master` Branch

1. Switch back to the `master` branch:
   ```bash
   git checkout master
   ```

2. Add an alpha commit:
   ```bash
   echo "Line Extra master: Add Alpha text" >> conflict.txt
   git add conflict.txt
   git commit -m "Alpha commit"
   ```

3. Display the file content:
   ```bash
   cat conflict.txt
   ```

4. Check the commit history:
   ```bash
   git log --oneline
   ```

### Explanation:
- `git checkout master`: Switches back to the `master` branch.
- `echo "Line Extra master: Add Alpha text" >> conflict.txt`: Appends a new line to `conflict.txt` in the `master` branch.
- `git add conflict.txt`: Stages the updated file for commit.
- `git commit -m "Alpha commit"`: Commits the staged changes with the message "Alpha commit."
- `cat conflict.txt`: Displays the current content of the file.
- `git log --oneline`: Shows a simplified commit history.

### Task 5: Merge `new_branch` into `master` and Resolve Conflict

1. Switch back to the `master` branch:
   ```bash
   git checkout master
   ```

2. Attempt to merge `new_branch` into `master`:
   ```bash
   git merge new_branch
   ```
   A merge conflict will occur because of the incompatible changes.

3. Manually resolve the conflict by editing the file to keep the lines you want. The conflict markers look like this:
   ```
   <<<<<<< HEAD
   Line 1: This is the start of the document.
   Line 2: Additional line in master branch.
   Line 3: Further changes in master branch.
   Line Extra master: Add Alpha text
   =======
   Line 1 (new branch): This line will cause a merge conflict.
   Line 2 (new branch): This is another conflicting line.
   >>>>>>> new_branch
   ```

4. After resolving the conflict, stage the changes:
   ```bash
   git add conflict.txt
   ```

5. Complete the merge with a commit:
   ```bash
   git commit -m "Resolved merge conflict between master and new_branch"
   ```

### Explanation:
- `git checkout master`: Ensures you are on the `master` branch.
- `git merge new_branch`: Attempts to merge `new_branch` into `master`, causing a conflict.
- Conflict markers `<<<<<<<`, `=======`, and `>>>>>>>` show the conflicting changes.
- Edit the file to resolve the conflict by keeping the desired lines.
- `git add conflict.txt`: Stages the resolved file.
- `git commit -m "Resolved merge conflict between master and new_branch"`: Commits the resolved merge.

### Conclusion

You have successfully created and resolved a merge conflict. This is a common situation when working on a team or when multiple changes happen to the same part of a file in different branches.