pipeline {
    agent any

    
    environment {
        DOCKER_CONTAINER_NAME = "lab_docker_jenkins-container"
        DOCKER_IMAGE_NAME     = "lab_docker_jenkins-image"
        PORT                  = "8085"
    }

    stages {
        stage('Initialize') {
            steps {
                echo 'Initial : Delete  containers and images'
                sh 'docker stop ${DOCKER_CONTAINER_NAME} || true'
                sh 'docker rm ${DOCKER_CONTAINER_NAME} || true'
                sh 'docker rmi ${DOCKER_IMAGE_NAME} || true'
              }
        }


        stage('Build Stage') {
            steps {
                dir('Lab_jenkins_docker') { // change directory to Lab_docker_Jenkins
                    echo "Current path is ${pwd()}"
                    sh "docker build -t ${DOCKER_IMAGE_NAME} ."
                }
            }
        }

        stage('Run Stage') {
            steps {
                sh "docker run -d -p ${PORT}:3000 --name ${DOCKER_CONTAINER_NAME} ${DOCKER_IMAGE_NAME}"
            }
        }

    
       

    }
}
