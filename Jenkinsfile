pipeline {
    agent any
    stages {
        stage('Build and Push Docker Images') {
            steps {
                script {
                    def services = ['db_postgresql', 'django_petproject', 'rabbitmq', 'celery_worker', 'celery_flower']

                    stage('Docker Login') {
                        withCredentials([usernamePassword(credentialsId: 'dockerhubaccount', passwordVariable: 'DOCKER_PASSWORD', usernameVariable: 'DOCKER_USERNAME')]) {
                            sh "docker login -u $DOCKER_USERNAME -p $DOCKER_PASSWORD"
                        }
                    }

                    for (service in services) {
                        stage("Build ${service}") {
                            sh "sudo docker-compose build ${service}"
                        }

                        stage("Push ${service}") {
                            sh "docker-compose push ${service}"
                        }
                    }
                }
            }
        }
    }

    post {
        always {
            // Завершение и очистка контейнеров после выполнения пайплайна
            script {
                def dockerComposeFile = './docker-compose.yml'

                // Остановка и удаление контейнеров
                sh "docker-compose -f ${dockerComposeFile} down"
            }
        }
    }
}
