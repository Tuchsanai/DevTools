

### Objective
Students will learn how to:
1. Initialize a new Git repository.
2. Rename the master branch to main.
3. Create and switch between multiple branches.
4. Add and commit files in different branches.
5. Push branches to a remote repository.
6. Understand the differences between local and remote logs.
7. Delete a remote branch and verify the remaining branches.

### Lab Instructions

#### 1. Initialize a New Git Repository
1. Open your terminal.
2. Create a new directory for your project:
    ```bash
    mkdir git-lab
    cd git-lab
    ```
    Explanation: `mkdir` creates a new directory called `git-lab`, and `cd git-lab` changes the current directory to `git-lab`.

3. Initialize a new Git repository:
    ```bash
    git init
    ```
    Explanation: `git init` initializes a new Git repository in the current directory.

#### 2. Rename the Master Branch to Main
1. Rename the master branch and start the first commit:
    ```bash
    git branch -m master main
    ```
    Explanation: `git branch -m master main` renames the default branch `master` to `main`.

    ```bash
    echo "This is main" > main.txt
    git add main.txt
    git commit -m "Initial commit on main branch"
    ```
    Explanation:
    - `echo "This is main" > main.txt` creates a new file named `main.txt` with the content "This is main".
    - `git add main.txt` stages the `main.txt` file for the next commit.
    - `git commit -m "Initial commit on main branch"` commits the staged changes with the message "Initial commit on main branch".

2. Verify the branch has been renamed:
    ```bash
    git status
    ```
    Explanation: `git status` shows the status of the working directory and staging area.

    ```bash
    git branch
    ```
    Explanation: `git branch` lists all the branches in the repository and highlights the current branch.

#### 3. Create and Switch Between Multiple Branches
1. Create 5 new branches:
    ```bash
    git branch branch1
    git branch branch2
    git branch branch3
    git branch branch4
    git branch branch5
    ```
    Explanation: `git branch branchX` creates a new branch named `branchX`.

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
    Explanation:
    - `git checkout branch1` switches to `branch1`.
    - `echo "This is file1 in branch1" > file1.txt` creates `file1.txt` in `branch1`.
    - `git add .` stages all changes in the current directory.
    - `git commit -m "Added files in branch1"` commits the changes with the message "Added files in branch1".
    - `echo "Current branch: $(git branch --show-current)"` prints the current branch name.

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
    Explanation:
    - `git switch main` switches to the `main` branch.
    - `echo "Current branch: $(git branch --show-current)"` prints the current branch name.

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
    Explanation: `git remote add origin <URL>` adds a remote repository with the name `origin`.

3. Push branches to the remote repository:
    ```bash
    git push -u origin main
    git push -u origin branch1
    git push -u origin branch2
    git push -u origin branch3
    git push -u origin branch4
    git push -u origin branch5
    ```
    Explanation: `git push -u origin branchX` pushes `branchX` to the remote repository and sets the upstream tracking reference.

#### 6. Understand the Differences Between Local and Remote Logs
1. View the local commit log:
    ```bash
    git log --oneline
    ```
    Explanation: `git log --oneline` shows the commit history in a compact form.

    ```bash
    git log 
    ```
    Explanation: `git log` shows the full commit history with details.

2. Fetch the latest changes from the remote repository:
    ```bash
    git fetch
    ```
    Explanation: `git fetch` retrieves the latest changes from the remote repository without merging them into the local branch.

3. View the remote commit log:
    ```bash
    git log origin/main --oneline
    ```
    Explanation: `git log origin/main --oneline` shows the commit history of the remote `main` branch in a compact form.

    ```bash
    git log origin/branch1 --oneline
    ```
    Explanation: `git log origin/branch1 --oneline` shows the commit history of the remote `branch1` in a compact form.

    ```bash
    git log origin/branch5 --oneline
    ```
    Explanation: `git log origin/branch5 --oneline` shows the commit history of the remote `branch5` in a compact form.

#### 7. Delete a Remote Branch and Verify Remaining Branches
1. To delete a remote branch, use the following command:
    ```bash
    git push origin --delete branch-name
    ```
    Explanation: `git push origin --delete branch-name` deletes the specified branch from the remote repository.

2. Verify the branch has been deleted from the remote repository:
    ```bash
    git fetch -p
    git branch -r
    ```
    Explanation:
    - `git fetch -p` fetches the latest updates from the remote repository and prunes any deleted branches.
    - `git branch -r` lists all remote branches.

3. Verify the remaining local branches:
    ```bash
    git branch
    ```
    Explanation: `git branch` lists all local branches.

