

### Lab Title: Exploring Git Reset - Soft and Hard

#### Objective:
To understand and practice the use of `git reset` with `soft` and `hard` options in Git.

#### Prerequisites:
- Basic understanding of command-line interface and Git commands.
- Git installed on the student's computer.

#### Lab Steps:

1. **Setup and Initialization**
   - Create a new directory and initialize a Git repository:
     ```bash
     mkdir git-reset-lab
     cd git-reset-lab
     git init
     ```

2. **First Commit**
   - Create a file and make the first commit:
     ```bash
     echo "First Commit Content" > file.txt
     git add file.txt
     git commit -m "First commit"
     ```

3. **Second Commit**
   - Update the file and make the second commit:
     ```bash
     echo "Second Commit Content" >> file.txt
     git add file.txt
     git commit -m "Second commit"
     ```

4. **Third Commit**
   - Append to the file and make the third commit:
     ```bash
     echo "Third Commit Content" >> file.txt
     git add file.txt
     git commit -m "Third commit"
     ```

5. **Fourth Commit**
   - Continue updating the file for the fourth commit:
     ```bash
     echo "Fourth Commit Content" >> file.txt
     git add file.txt
     git commit -m "Fourth commit"
     ```

6. **Fifth Commit**
   - Finally, make the fifth commit:
     ```bash
     echo "Fifth Commit Content" >> file.txt
     git add file.txt
     git commit -m "Fifth commit"
     ```

7. **Using Git Reset Soft**
   - Reset to the third commit using the `soft` option:
     ```bash
     git reset --soft <commit-hash-of-third-commit>
     ```
   - Instruct students to observe the staging area and commit history.

8. **Using Git Reset Hard**
   - Next, reset to the first commit using the `hard` option:
     ```bash
     git reset --hard <commit-hash-of-first-commit>
     ```
   