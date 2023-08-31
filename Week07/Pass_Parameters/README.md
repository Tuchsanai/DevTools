# Slaves

```
pipeline {
    agent any
    parameters {
        string(name: 'NAME', defaultValue: 'Tuchsanai', description: 'Enter your name')
        choice(name: 'CITY', choices: ['Bangkok','Bebbanburg', 'Mercia', 'East Anglia'], description: 'Choose your city')
    }
    stages {
        stage('Example') {
            steps {
                echo "Hello from Slave ${params.NAME} of ${params.CITY}"
                
            }
        }
    }
}
```


# Master
```
pipeline {
    agent any

    stages {
        
        stage('Welcome to master'){
            steps{
                echo 'Start Program'
            }
        }

        stage('Tigger the Slave Jobs') {
            steps {
                echo 'Start Trigger'
                build job: 'slave', parameters: [string(name: 'NAME', value: 'Tuchsanai'), string(name: 'CITY', value: 'Mercia')]
            }
        }
    }
}

```


To see complete list of parameters, you may refer https://www.jenkins.io/doc/book/pipeline/syntax/#parameters

