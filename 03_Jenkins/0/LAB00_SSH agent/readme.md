```
pipeline {
    agent any

    stages {
        
        stage('Jenkins Public IP') {
            steps {
                script {
                    // Use a shell command to get the public IP address
                    def ip = sh(script: 'curl -s ifconfig.me', returnStdout: true).trim()
                    echo "Jenkins Public IP Address: ${ip}"
                }
            } 
        }    
        
        stage('Apply multiple Commands') {
            steps {
                sshagent(['agent_id'])  {
                   
                    sh '''
                        ssh -o StrictHostKeyChecking=no remote_user@remote_host
                            echo First command;
                            echo Second command;
                            echo Third command
                    '''
                    // Replace remote_user, remote_host, and the commands with your own.
                }
            }
        }
    }
}




```