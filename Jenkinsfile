pipeline{
    agent any
    stages {
        stage('Build'){
            steps  {
                sh 'docker compose build'
                }
            }
        stage('Test'){
            steps {
                sh 'docker compose up -d'
                
                sh 'sleep 10'
                
                sh 'docker compose run django_petproject python manage.py makemigrations'
                sh 'docker compose run django_petproject python manage.py migrate'
                
                sh 'docker compose exec django_petproject pytest'
                
                sh 'docker compose down'

                }
            }
       }
    }
