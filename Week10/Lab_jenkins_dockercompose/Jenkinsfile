pipeline {
    agent any

 
    stages {
        stage('Initialize Stage') {
            steps {
            
                echo 'Initial : Delete  containers and images'
                 dir('Lab_jenkins_dockercompose') { // change directory to Lab_docker_Jenkins
                    echo "Current path is ${pwd()}"
                    sh "docker-compose down --rmi all --volumes || true"
                }
            }
        }


        stage('Build Stage') {
            steps {
                dir('Lab_jenkins_dockercompose') { // change directory to Lab_docker_Jenkins
                    echo "Current path is ${pwd()}"
                    sh "docker-compose up -d"
                }
            }
        }

    
       

    }
}
