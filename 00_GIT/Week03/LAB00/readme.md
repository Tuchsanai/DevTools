### Objective
Students will learn how to:
1. Initialize a new Git repository.
2. Rename the master branch to main.
3. Create and switch between multiple branches.
4. Add and commit files in different branches.
5. Push branches to a remote repository.
6. Understand the differences between local and remote logs.
7. Delete a remote branch.

### Lab Instructions

#### 1. Initialize a New Git Repository
1. Open your terminal.
2. Create a new directory for your project:
    ```bash
    mkdir git-lab
    cd git-lab
    ```
3. Initialize a new Git repository:
    ```bash
    git init
    ```

#### 2. Rename the Master Branch to Main
1. Rename the master branch and start the first commit:
    ```bash
    git branch -m master main
    ```
    ```bash
    echo "This is main" > main.txt
    git add main.txt
    git commit -m "Initial commit on main branch"
    ```

2. Verify the branch has been renamed:
    ```bash
    git status
    ```
    ```bash
    git branch
    ```

#### 3. Create and Switch Between Multiple Branches
1. Create 5 new branches:
    ```bash
    git branch branch1
    git branch branch2
    git branch branch3
    git branch branch4
    git branch branch5
    ```
2. Switch to each branch, create files, and display the current branch (Note: You can use `git checkout` or `git switch` to switch branches):
    ```bash
    git checkout branch1
    echo "This is file1 in branch1" > file1.txt
    echo "This is file2 in branch1" > file2.txt
    echo "This is file3 in branch1" > file3.txt
    git add .
    git commit -m "Added files in branch1"
    echo "Current branch: $(git branch --show-current)"
    ```

    ```bash
    git checkout branch2
    echo "This is file1 in branch2" > file1.txt
    echo "This is file2 in branch2" > file2.txt
    echo "This is file3 in branch2" > file3.txt
    git add .
    git commit -m "Added files in branch2"
    echo "Current branch: $(git branch --show-current)"
    ```

    ```bash
    git checkout branch3
    echo "This is file1 in branch3" > file1.txt
    echo "This is file2 in branch3" > file2.txt
    echo "This is file3 in branch3" > file3.txt
    git add .
    git commit -m "Added files in branch3"
    echo "Current branch: $(git branch --show-current)"
    ```

    ```bash
    git checkout branch4
    echo "This is file1 in branch4" > file1.txt
    echo "This is file2 in branch4" > file2.txt
    echo "This is file3 in branch4" > file3.txt
    git add .
    git commit -m "Added files in branch4"
    echo "Current branch: $(git branch --show-current)"
    ```

    ```bash
    git checkout branch5
    echo "This is file1 in branch5" > file1.txt
    echo "This is file2 in branch5" > file2.txt
    echo "This is file3 in branch5" > file3.txt
    git add .
    git commit -m "Added files in branch5"
    echo "Current branch: $(git branch --show-current)"
    ```

#### 4. Switch Between Branches Using `git switch` and `git checkout`
1. Switch back to the `main` branch using `git switch`:
    ```bash
    git switch main
    echo "Current branch: $(git branch --show-current)"
    ```
2. Switch to `branch1` using `git switch`:
    ```bash
    git switch branch1
    echo "Current branch: $(git branch --show-current)"
    ```
3. Switch back to the `main` branch using `git checkout`:
    ```bash
    git checkout main
    echo "Current branch: $(git branch --show-current)"
    ```
4. Switch to `branch2` using `git checkout`:
    ```bash
    git checkout branch2
    echo "Current branch: $(git branch --show-current)"
    ```

#### 5. Push Branches to a Remote Repository
1. Create a new repository on GitHub (or any other Git hosting service).
2. Add the remote repository:
    ```bash
    git remote add origin <your-remote-repository-URL>
    ```
3. Push branches to the remote repository:
    ```bash
    git push -u origin main
    git push -u origin branch1
    git push -u origin branch2
    git push -u origin branch3
    git push -u origin branch4
    git push -u origin branch5
    ```

#### 6. Understand the Differences Between Local and Remote Logs
1. View the local commit log:
    ```bash
    git log --oneline
    ```
    ```bash
    git log 
    ```
2. Fetch the latest changes from the remote repository:
    ```bash
    git fetch
    ```
3. View the remote commit log:
    ```bash
    git log origin/main --oneline
    ```
    ```bash
    git log origin/branch1 --oneline
    ```
    ```bash
    git log origin/branch5 --oneline
    ```

#### 7. Delete a Remote Branch
1. To delete a remote branch, use the following command:
    ```bash
    git push origin --delete branch-name
    ```

### Summary
By the end of this lab, students should be able to:
- Initialize a Git repository and rename branches.
- Create and switch between branches.
- Add, commit, and push changes to a remote repository.
- Understand the difference between local and remote logs.
- Delete a remote branch.

Encourage students to ask questions and experiment with additional Git commands to deepen their understanding.