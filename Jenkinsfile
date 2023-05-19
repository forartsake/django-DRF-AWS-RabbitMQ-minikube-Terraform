pipeline {
    agent any
    
    stages {
        stage('Build') {
            steps {
                script {
                    // Определение пути до файла docker-compose.yml
                    def dockerComposeFile = './docker-compose.yml'
                    
                    // Запуск команды docker-compose up для сборки контейнеров
                    sh "docker-compose -f ${dockerComposeFile} up -d"
                    
                    // Проверка статуса контейнеров
                    def containerStatus = sh(script: "docker-compose -f ${dockerComposeFile} ps -q | xargs docker inspect -f '{{ .State.Status }}'", returnStdout: true)
                    
                    // Проверка, успешно ли запущены все контейнеры
                    if (containerStatus.trim().contains('running')) {
                        echo 'Все контейнеры были успешно запущены.'
                    } else {
                        error 'Не удалось запустить все контейнеры.'
                    }
                }
            }
        }
        
        stage('Test') {
            steps {
                script {        
                    // Запуск тестов с помощью pytest
                    sh 'pytest'
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
