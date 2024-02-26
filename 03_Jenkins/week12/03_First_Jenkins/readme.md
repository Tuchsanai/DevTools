
First Jenkins Pipeline
```

pipeline {
    agent any  // Execute on any available Jenkins agent

    stages {
        stage('Hello World') {
            steps {
                sh  'echo Hello World!'
            }
        }
    }
}




```
