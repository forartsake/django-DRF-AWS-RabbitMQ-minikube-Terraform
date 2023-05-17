pipeline{
    agent any
    stages {
        stage('Build the containers'){
            steps  {
                sh "docker-compose build -up"
                }
            }
        stage('Test'){
            steps {
                sh 'docker-compose build -up'
                sh 'docker start petproject'
                sh 'docker start pet_postgres'
                sh 'docker exec -i django apk add --no-cache bash'
                sh 'docker exec -i django bash -c "pytest"'
                }
            }
       }
    }
//         stage('Linters with flake8'){
//             steps {
// //                 sh "docker-compose build -up",
//                 sh "docker exec --interactive --tty --user root django bash -c 'flake8 .'"
//             }
//         }