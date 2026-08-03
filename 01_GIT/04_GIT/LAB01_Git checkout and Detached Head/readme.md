

### Git Lab Exercise: Git checkout and Detached Head

#### Objective
This lab will guide you through using `git checkout` to navigate between commits, using `git log --oneline` to view a concise commit history, and understanding the concept of a detached head in Git. You will create and navigate through a series of five commits.

#### Setup
1. **Initialize a New Git Repository:**
   Open your terminal and run the following commands to create a new repository:

   ```bash
   git init GitCheckoutLab
   cd GitCheckoutLab
   ```

2. **Create an Initial File and Commit:**
   Create your first file and make the initial commit:

   ```bash
   echo "Initial line in the file." > example.txt
   git add example.txt
   git commit -m "Initial commit"
   ```

#### Tasks
1. **Make Four Additional Commits:**
   You will add new content to `example.txt` and make four more commits. Here's how to proceed:

   - **Second Commit:**
     ```bash
     echo "Second line in the file." >> example.txt
     git commit -am "Second commit"
     ```

   - **Third Commit:**
     ```bash
     echo "Third line added." >> example.txt
     git commit -am "Third commit"
     ```

   - **Fourth Commit:**
     ```bash
     echo "Fourth line now." >> example.txt
     git commit -am "Fourth commit"
     ```

   - **Fifth Commit:**
     ```bash
     echo "Finally, the fifth line." >> example.txt
     git commit -am "Fifth commit"
     ```

2. **View the Commit History with `git log --oneline`:**
   After your five commits, run the following command to view a summarized commit history:

   ```bash
   git log --oneline
   ```

3. **Checkout to Specific Commits and Explore:**
   - **Checkout to the Third Commit:**
     Find and use the hash of the third commit to switch to it:

     ```bash
     git checkout <hash-of-third-commit>
     ```

   - **Explore Detached Head State:**
     While in this state, observe the contents and status of your repository.

   - **Return to the Latest Commit:**
     Checkout back to the latest commit on your main branch:

     ```bash
     git checkout main or git checkout master

     ```

   - **Checkout to the First Commit:**
     Finally, checkout to the first commit using its commit hash.

#### Deliverables
- Submit a report detailing your process, observations in the detached head state, and changes in the repository at different commit stages.
- Discuss the utility of `git log --oneline` and how it assists in understanding the history of changes in a project.
