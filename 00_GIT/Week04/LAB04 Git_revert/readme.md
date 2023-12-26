

### Git Lab Exercise: Understanding `git revert`

#### Objective
Learn to effectively use the `git revert` command to undo changes in a Git repository. This lab will involve making five distinct commits and using `git revert` to undo some of these changes.

#### Setup
1. **Initialize a New Git Repository:**
   Begin by creating a new Git repository in your terminal:

   ```bash
   git init GitRevertLab
   cd GitRevertLab
   ```

2. **Sequential File Creation and Committing:**
   Here are the steps for each of the five commits:

   - **Commit 1:**
     ```bash
     echo "Initial content in file1" > file1.txt
     git add file1.txt
     git commit -m "Initial commit of file1"
     ```

   - **Commit 2:**
     ```bash
     echo "Initial content in file2" > file2.txt
     git add file2.txt
     git commit -m "Add file2"
     ```

   - **Commit 3:**
     ```bash
     echo "Update to file1" >> file1.txt
     git add file1.txt
     git commit -m "Update file1"
     ```

   - **Commit 4:**
     ```bash
     echo "Update to file2" >> file2.txt
     git add file2.txt
     git commit -m "Update file2"
     ```

   - **Commit 5:**
     ```bash
     echo "Final update to file1" >> file1.txt
     git add file1.txt
     git commit -m "Final update file1"
     ```

#### Tasks
1. **Use `git log` to View Commit History:**
   Familiarize yourself with the commit history to understand the changes made:

   ```bash
   git log --oneline
   ```

2. **Revert Specific Commits:** : Don't worry if there are merge conflicts. We will resolve them in the next step.
   Choose a commit to revert. For example, revert the third commit:

   ```bash
   git revert <commit-hash-of-third-commit>
   # Follow prompts to complete the revert
   git log --oneline  # Verify the revert
   ```

   Repeat this process for other commits you wish to revert.

3. **Resolve Conflicts if They Occur:**
   If a revert causes conflicts, resolve them manually, then complete the revert:

   ```bash
   # Edit the conflicted files
   git add .
   git revert --continue
   git log --oneline  # Verify the revert
   ```


#### Conclusion
This lab is aimed at providing a hands-on understanding of `git revert` and its impact on a Git repository, emphasizing its role in undoing changes and managing the project's history.

