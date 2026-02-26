pipeline {
    agent any

    environment {
        // It's good practice to keep sensitive or specific data like Docker images, remote hosts, and credentials out of the script for security and flexibility.
        DOCKER_IMAGE    = 'tuchsanai/fastapi-webhook:latest' // Ensure this Docker image name is correct and accessible.
        REMOTE_HOST     = 'tuchsanai@34.124.197.62' // Replace with your actual username and remote IP.
        SSH_CREDENTIALS = 'ssh_prod_instance' // Use the ID of the Jenkins stored SSH credentials.
    }

    stages {
        stage('Login to Docker Hub') {
            steps {
                // This step logs into Docker Hub using credentials stored in Jenkins.
                withCredentials([usernamePassword(credentialsId: 'dockerhub', passwordVariable: 'DOCKERHUB_PASSWORD', usernameVariable: 'DOCKERHUB_USER')]) {
                    sh 'echo $DOCKERHUB_PASSWORD | docker login --username $DOCKERHUB_USER --password-stdin'
                }
            }
        }

        stage('Run Docker on Remote Server') {
            steps {
                sshagent([SSH_CREDENTIALS]) {
                    script {
                        def commands = [
                            'docker stop $(docker ps -a -q) || true',
                            'docker rm $(docker ps -a -q) || true',
                            'docker rmi $(docker images -q) || true',
                            "docker run -d --name fastapi-webhook -p 8085:80 ${DOCKER_IMAGE}",
                            'docker ps -a'
                        ]
                        
                        commands.each { cmd ->
                            sh "ssh -o StrictHostKeyChecking=no ${REMOTE_HOST} '${cmd}'"
                        }
                    }
                }
            }
        }
    }
}
