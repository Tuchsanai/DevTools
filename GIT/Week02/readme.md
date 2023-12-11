

### 1. Create a New Directory (Lab Folder)
First, create a new directory which will serve as your lab environment. Open your command line interface (CLI) and run:

```bash
mkdir git-lab
cd git-lab
```

This creates a new folder named `git-lab` and changes your current directory to `git-lab`.

### 2. Initialize a Git Repository
Inside the `git-lab` directory, initialize a new Git repository:

```bash
git init
```

This command creates a new Git repository in the current directory.

### 3. Create Three Files
Now, create three sample files. You can use a text editor or simply use the `echo` command for simplicity:

```bash
echo "This is file 1" > file1.txt
echo "This is file 2" > file2.txt
echo "This is file 3" > file3.txt
```

This will create three text files named `file1.txt`, `file2.txt`, and `file3.txt` with basic content in each.

### 4. Add Files to the Staging Area
To include these files in your next commit, you need to add them to the staging area:

```bash
git add file1.txt file2.txt file3.txt
```

Alternatively, you can use `git add .` to add all new and modified files in the current directory to the staging area.

### 5. Commit the Changes
Now, commit these changes to the repository with a commit message:

```bash
git commit -m "Initial commit with three files"
```

This saves the changes in the repository with the provided commit message.

### 6. Verify the Commit
To ensure everything is committed correctly, you can check the status and log:

```bash
git status
git log
```

`git status` shows the current state of the repository, and `git log` displays the commit history.

### Conclusion
You've successfully created a lab environment with a Git repository, added three files, and committed them to the repository. This setup can be used for teaching basic Git operations in a devops or AI machine learning context.