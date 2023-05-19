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
                    // Проверка наличия контейнера с PostgreSQL
                    def postgresContainer = sh(script: "docker-compose ps -q db_postgresql", returnStdout: true).trim()
                    
                    if (postgresContainer) {
                        echo "Контейнер с PostgreSQL запущен."
                    } else {
                        error "Контейнер с PostgreSQL не найден."
                    }
                     // Выполнение миграций
                    sh "docker exec -i petproject python manage.py makemigrations"
                    sh "docker exec -i petproject python manage.py migrate"
                     // Проверка таблиц в базе данных
                    def result = sh(script: 'docker exec -it pet_postgres psql -U postgres -c "SELECT table_name FROM information_schema.tables WHERE table_schema = \'public\';"', returnStdout: true).trim()
                    echo "Список таблиц в базе данных:"
                    echo result
                    // Запуск тестов с помощью pytest
                    sh "docker exec -i petproject pytest"
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
