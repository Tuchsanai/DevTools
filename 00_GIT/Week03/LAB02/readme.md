### Step-by-Step Explanation of the Lab

#### Step 1: Initialize a New Git Repository and Make the First Commit

1. **Create a new directory for the repository:**
   ```bash
   mkdir my-git-repo
   cd my-git-repo
   ```
   - **Explanation:** This creates a new directory called `my-git-repo` and changes the current directory to it. This is where your Git repository will reside.

2. **Initialize the Git repository:**
   ```bash
   git init
   ```
   - **Explanation:** Initializes an empty Git repository in the `my-git-repo` directory.

3. **Create a new file and make the first commit:**
   ```bash
   echo "Initial commit" > file1.txt
   git add file1.txt
   git commit -m "Initial commit"
   ```
   - **Explanation:** Creates a new file named `file1.txt` with the content "Initial commit", adds it to the staging area, and commits it to the repository with the message "Initial commit".

#### Step 2: Rename the Master Branch to Main

1. **Rename the branch:**
   ```bash
   git branch -M main
   ```
   - **Explanation:** Renames the current branch (which is `master` by default) to `main`.

#### Step 3: Create Two New Branches with At Least Three Commits Each

1. **Create the first branch (`feature-1`) and make three commits:**
   ```bash
   git checkout -b feature-1
   echo "Feature 1 - Commit 1" > feature1.txt
   git add feature1.txt
   git commit -m "Feature 1 - Commit 1"

   echo "Feature 1 - Commit 2" >> feature1.txt
   git add feature1.txt
   git commit -m "Feature 1 - Commit 2"

   echo "Feature 1 - Commit 3" >> feature1.txt
   git add feature1.txt
   git commit -m "Feature 1 - Commit 3"
   ```
   - **Explanation:** Creates a new branch named `feature-1` and switches to it. Then, it creates a file named `feature1.txt` and makes three commits with different changes to this file.

2. **Create the second branch (`feature-2`) and make three commits:**
   ```bash
   git checkout main
   git checkout -b feature-2
   echo "Feature 2 - Commit 1" > feature2.txt
   git add feature2.txt
   git commit -m "Feature 2 - Commit 1"

   echo "Feature 2 - Commit 2" >> feature2.txt
   git add feature2.txt
   git commit -m "Feature 2 - Commit 2"

   echo "Feature 2 - Commit 3" >> feature2.txt
   git add feature2.txt
   git commit -m "Feature 2 - Commit 3"
   ```
   - **Explanation:** Switches back to the `main` branch, then creates another new branch named `feature-2` and switches to it. Similar to `feature-1`, it creates a file named `feature2.txt` and makes three commits with different changes to this file.

#### Step 4: Merge Branches Without Conflict

1. **Merge `feature-1` into `main`:**
   ```bash
   git checkout main
   git merge feature-1
   ```
   - **Explanation:** Switches back to the `main` branch and merges the changes from `feature-1` into `main`. Since there are no conflicting changes, the merge should complete successfully.

2. **Verify the merge:**
   ```bash
   git log --oneline --graph
   ```
   - **Explanation:** Displays a log of commits with a graphical representation to show the commit history and how the branches were merged.

#### Step 5: Switch to the Last Commit in the First Branch from Main and Delete the Branch

1. **Checkout the last commit of `feature-1`:**
   ```bash
   git checkout feature-1
   git log --oneline --graph
   git checkout main
   ```
   - **Explanation:** Switches to the `feature-1` branch to view its commit history and then back to the `main` branch.

2. **Delete the `feature-1` branch:**
   ```bash
   git branch -d feature-1
   ```
   - **Explanation:** Deletes the `feature-1` branch. The `-d` option deletes the branch only if it has been fully merged.

#### Step 6: Focus on the Second Branch (Experimental)

1. **Switch to the `feature-2` branch:**
   ```bash
   git checkout feature-2
   ```
   - **Explanation:** Switches to the `feature-2` branch to start working on it.

2. **Attempt to delete `feature-2` branch while checked out (should cause an error):**
   ```bash
   git branch -d feature-2
   ```
   - **Explanation:** Attempts to delete the currently checked-out branch (`feature-2`). This should result in an error because you cannot delete the branch you are currently on.

3. **Force delete `feature-2` branch:**
   ```bash
   git checkout main
   git branch -d feature-2
   ```
    - **Explanation:** this may fail if the branch has unmerged changes.


   ```bash
   git checkout main
   git branch -D feature-2
   ```
  
   - **Explanation:** Switches back to the `main` branch and force deletes the `feature-2` branch using the `-D` option, which deletes the branch regardless of its merge status.

#### Step 7: Complete the Task by Viewing the Full Git Log

1. **View the full Git log:**
   ```bash
   git log --oneline --graph --all
   ```
   - **Explanation:** Displays a complete log of all commits in the repository, including those from deleted branches, with a graphical representation to show the entire commit history.

By completing this lab, students will learn how to initialize a Git repository, create and manage branches, make commits, merge branches without conflicts, and handle branch deletion. Additionally, they will gain experience in viewing the full commit history using Git log.