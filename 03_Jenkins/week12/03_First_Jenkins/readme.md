
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

- if sucess you will see the following output:

[![Jenkins Pipeline](https://img.youtube.com/vi/3zv3n3j3y9E/0.jpg)](https://www.youtube.com/watch?v=3zv3n3j3y9E)
