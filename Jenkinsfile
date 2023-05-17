pipeline {
    agent any
    
    stages {
        stage('Build Docker images') {
            steps {
                script {
                    sh "docker compose build"
                }
            }
        }
    }
}

