# Pipeline using Pipeline script


Enter script
        

Linux
```
   pipeline {
   agent any
    stages {
        stage('build') {
            steps {
                
                sh 'echo welcome to first pipeline'
                sh 'python3 -version'
            }
        }
    }
}
```
