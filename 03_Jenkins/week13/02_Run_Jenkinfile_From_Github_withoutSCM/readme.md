# Jenkins file with GitHub
# - detail in slides 

```
pipeline {
    agent any

    stages {

       stage('copy repository') {
            steps {

                 //  Copy the repository 
                 checkout scmGit(branches: [[name: '*/dev']], extensions: [], userRemoteConfigs: [[credentialsId: 'github', url: 'https://github.com/Tuchsanai/DevTools.git']])

            }  
       }

        stage('Check Python Installation') {
            steps {
                script {
                    // Check if Python is installed
                    def pythonInstalled = sh(script: "which python3", returnStatus: true) == 0
                    if (!pythonInstalled) {
                        // Install Python if not installed
                        sh 'sudo apt update'
                        sh 'sudo apt install -y python3'
                    }
                }
            }
        }

        stage('Run Python Script') {
            steps {
                script {
                    // Run Python script with only os library
                    sh 'pwd'
                    sh 'python3  ./03_Jenkins/week13/02_Run_Jenkinfile_From_Github_withoutSCM/status.py'


                    
                    sh 'ls -l'
                }
            }

        } 
        
    }

}    

```


