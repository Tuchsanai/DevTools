

```

pipeline {
    agent any  // Execute on any available Jenkins agent

    stages {
        stage('Hello World') {
            steps {
                echo 'Hello World!'
            }
        }
    }
}


```