

### Git Lab Exercise: Proficiency with `git restore`

#### Objective
Develop a comprehensive understanding of the `git restore` command in Git through a series of hands-on exercises. This lab includes making five distinct commits, followed by operations using `git restore`, and understanding the repository's state with `git log` and `git status`.

The diagram below shows the two forms of `git restore` you will practice in this lab:

![Overview of git restore](images/git-restore-overview.svg)

#### Setup
1. **Initialize a New Git Repository:**
   Begin by creating a new Git repository in your terminal:

   ```bash
   git init GitRestoreLab
   cd GitRestoreLab
   ```

   ```bash
   git init 
   ```

2. **Create Files and Commit Sequentially:**
   Follow these steps for each of the five commits:

   - **Commit :**
     ```bash
     echo "Initial content in file1" > file1.txt
     git add file1.txt
     git commit -m "Initial commit of file1"
     ```

   - **Commit :**
     ```bash
     echo "Initial content in file2" > file2.txt
     git add file2.txt
     git commit -m "Add file2"
     ```

   - **Commit :**
   ```bash
      echo "Update to file1" >> file1.txt
      git add file1.txt
      git commit -m "Update file1"
   ```
   ```bash
      echo "Update to file2" >> file2.txt
      git add file2.txt
      git commit -m "Update file2"
   ```



- **Commit :**
   ```bash
      echo "Initial content in file3" > file3.txt
      git add file3.txt
      git commit -m "Initial commit of file3"
   ```
   ```bash
      echo "Update to file3" >> file3.txt
      git add file3.txt
      git commit -m "Update file3"
   ```


- **Commit :**
    ```bash
     echo "xxxx More xxxx Update to file3" >> file3.txt
     git add file3.txt
     git commit -m "Update xxx More xxx file3"
    ```

   

#### Tasks
1. **Use `git log` and `git status`:**
   After each operation, examine the commit history and current status:

   ```bash
   git log --oneline
   git status
   ```

   ✅ **Expected output** (your commit hashes will be different):

   ```text
   $ git log --oneline
   f9a01b8 Update xxx More xxx file3
   9f170ba Update file3
   8b9a4ce Initial commit of file3
   452a9fb Update file2
   2441c7a Update file1
   b963520 Add file2
   8cdace8 Initial commit of file1

   $ git status
   On branch master
   nothing to commit, working tree clean
   ```

2. **Practice Using `git restore` with HEAD:**
   Modify a file and revert the changes using `HEAD`:

   ```bash
   echo "Additional line in file1" >> file1.txt
   git status  # Check the effect
   git log --oneline  # Check the effect
   ```

   ✅ **Expected output** — `file1.txt` is now **modified** (but `git log` does not change, because nothing was committed):

   ```text
   $ git status
   On branch master
   Changes not staged for commit:
     (use "git add <file>..." to update what will be committed)
     (use "git restore <file>..." to discard changes in working directory)
           modified:   file1.txt

   no changes added to commit (use "git add" and/or "git commit -a")

   $ cat file1.txt
   Initial content in file1
   Update to file1
   Additional line in file1
   ```

  ```bash
   git restore --source=HEAD file1.txt
   git status  # Check the effect
   git log --oneline  # Check the effect
   ```

   ✅ **Expected output** — the extra line is gone and the working tree is clean again:

   ```text
   $ cat file1.txt
   Initial content in file1
   Update to file1

   $ git status
   On branch master
   nothing to commit, working tree clean
   ```



3. **Restore to Specific Commit and HEAD~3:**
   Alter a file and restore it to an earlier commit:

   ```bash
   echo "More Change in file2" >> file2.txt
   ```

   Before choosing `N`, look at the history again. `HEAD~N` means "N commits **before** the latest commit":

   ![How HEAD~N maps to the commit history](images/head-tilde-map.svg)

   ** try to change N = 1,2,3..
   ```bash
   git restore --source=HEAD~N file2.txt
   ```

   ✅ **Expected output** — after adding the line, `file2.txt` has 3 lines:

   ```text
   $ cat file2.txt
   Initial content in file2
   Update to file2
   More Change in file2
   ```

   With `N = 1` the extra line disappears, because `file2.txt` in commit `HEAD~1` still had only 2 lines:

   ```text
   $ git restore --source=HEAD~1 file2.txt
   $ cat file2.txt
   Initial content in file2
   Update to file2
   ```

   With `N = 4` the file goes all the way back to its **initial content** (commit "Update file1" happened *before* "Update file2"), and `git status` reports the file as modified because it now differs from `HEAD`:

   ```text
   $ git restore --source=HEAD~4 file2.txt
   $ cat file2.txt
   Initial content in file2

   $ git status
   On branch master
   Changes not staged for commit:
     (use "git add <file>..." to update what will be committed)
     (use "git restore <file>..." to discard changes in working directory)
           modified:   file2.txt

   no changes added to commit (use "git add" and/or "git commit -a")
   ```

   You can bring the file back to the latest committed version at any time:

   ```text
   $ git restore --source=HEAD file2.txt
   $ cat file2.txt
   Initial content in file2
   Update to file2
   ```



4. **Stage Changes and Explore `git restore --staged`:**
   Stage changes in a file and then unstage them:

   ```bash
   echo "Further changes in file3" >> file3.txt
   git add file3.txt
   git status  # Verify staged
   ```

   ✅ **Expected output** — the change is **staged** (ready to be committed):

   ```text
   $ git status
   On branch master
   Changes to be committed:
     (use "git restore --staged <file>..." to unstage)
           modified:   file3.txt
   ```

  ```bash
   git restore --staged file3.txt
   git status  # Verify unstage
   ```

   ✅ **Expected output** — the file is **unstaged**, but notice that your change is still in the file (`git restore --staged` only touches the staging area, not the working directory):

   ```text
   $ git status
   On branch master
   Changes not staged for commit:
     (use "git add <file>..." to update what will be committed)
     (use "git restore <file>..." to discard changes in working directory)
           modified:   file3.txt

   no changes added to commit (use "git add" and/or "git commit -a")

   $ cat file3.txt
   Initial content in file3
   Update to file3
   xxxx More xxxx Update to file3
   Further changes in file3
   ```


#### Deliverables
- A detailed report documenting each step, the `git` commands used, and the outcomes observed.
- Analysis of the role of `git log` and `git status` in managing repository changes.

#### Conclusion
This lab is designed to provide a deep understanding of `git restore`, emphasizing its importance in precise version control and repository management in Git.
