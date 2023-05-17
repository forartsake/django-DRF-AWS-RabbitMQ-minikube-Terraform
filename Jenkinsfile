pipeline {
    agent any
    stages {
        stage('Build the containers') {
            steps {
                sh 'docker-compose build && docker-compose up -d'
            }
        }
        stage('Test') {
            steps {
                sh 'docker start petproject'
                sh 'docker start pet_postgres'
                sh 'docker exec -i django apk add --no-cache bash'
                sh 'docker exec -i django bash -c "pytest"'
            }
        }
    }
    post {
        always {
            sh 'docker-compose down'
        }
    }
}
//         stage('Linters with flake8'){
//             steps {
// //                 sh "docker-compose build -up",
//                 sh "docker exec --interactive --tty --user root django bash -c 'flake8 .'"
//             }
//         }
