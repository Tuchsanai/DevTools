# Parallel steps in a stage



```
pipeline {
    agent any
    stages {
        stage('pre -build') {
            steps {
                bat 'echo Pre-build'
            }
        }
        stage('build') {
            steps {
                bat 'echo Build in progress.'
            }
        }
        stage('Unit tests') {
            steps {
                bat 'echo Running unit tests'
            }
        }
        stage('deploy') {
            steps {
                bat 'echo Deploying build'
            }
        }
        stage('Regression tests') {
            steps {
                parallel{
                        stage('chrome') {
                            steps {
                                bat 'echo Running E2E tests on chrome'
                            }
                        }
                        stage('firefox') {
                            steps {
                                bat 'echo Running E2E tests on chrome'
                            }
                        }
                        stage('safari') {
                            steps {
                                bat 'echo Running E2E tests on chrome'
                            }
                        }
                }
            }
        }
        stage('Release to prod') {
            steps {
                bat 'echo Releasing to prod'
            }
        }
    }
 post {
        always {
            echo 'Cleanup after everything!'
        }
    }
}
```
