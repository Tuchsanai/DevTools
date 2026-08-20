pipeline {
  agent any

  stages {
    stage('Source') {
      steps {
        echo 'Jenkinsfile loaded from student/hello-ci on branch main'
        sh 'git log -1 --oneline'
      }
    }
    stage('Validate') {
      steps {
        sh 'test -x hello.sh && test -s expected.txt'
      }
    }
    stage('Test') {
      steps {
        sh './hello.sh | tee actual.txt'
        sh 'diff -u expected.txt actual.txt'
      }
    }
    stage('Report') {
      steps {
        echo 'Lightweight test passed; no image was pushed'
      }
    }
  }
}
