// pipeline {
// <<<<<<< HEAD
//     agent any
//
//     stages {
//         stage('Build') {
//             steps {
//                 script {
//                     // Определение пути до файла docker-compose.yml
//                     def dockerComposeFile = './docker-compose.yml'
//
//                     // Запуск команды docker-compose up для сборки контейнеров
//                     sh "docker-compose -f ${dockerComposeFile} up -d"
//                        // Ожидание некоторого времени, чтобы контейнеры успели запуститься
//
//
//                     // Вывод журналов контейнеров
//                     sh "docker-compose -f ${dockerComposeFile} logs"
//
//                     // Проверка статуса контейнеров
//                     def containerStatus = sh(script: "docker-compose -f ${dockerComposeFile} ps -q | xargs docker inspect -f '{{ .State.Status }}'", returnStdout: true)
//
//                     // Проверка, успешно ли запущены все контейнеры
//                     if (containerStatus.trim().contains('running')) {
//                         echo 'Все контейнеры были успешно запущены.'
//                     } else {
//                         error 'Не удалось запустить все контейнеры.'
//                     }
//                 }
//             }
//         }
//
//         stage('Test') {
//             steps {
//                 script {
//                     // Проверка наличия контейнера с PostgreSQL
//                     def postgresContainer = sh(script: "docker-compose ps -q db_postgresql", returnStdout: true).trim()
//
//                     if (postgresContainer) {
//                         echo "Контейнер с PostgreSQL запущен."
//                         // Вывод списка таблиц
//                         sh "docker exec -i pet_postgres psql -U postgres -c '\\dt'"
//                     } else {
//                         error "Контейнер с PostgreSQL не найден."
//                     }
//                     sh 'sleep 15'
//                     // Запуск тестов с помощью pytest
//                     sh "docker exec -i petproject python manage.py makemigrations"
//                     sh "docker exec -i petproject python manage.py migrate"
//                     sh "docker exec -i petproject python manage.py migrate django_celery_results"
//
//
//                     sh "docker exec -i petproject pytest"
//                 }
//             }
//         }
//     }
//         stage('Publish to Docker Hub') {
//             steps {
//                 script {
//                     withCredentials([usernamePassword(credentialsId: 'docker-hub-credentials', passwordVariable: 'DOCKER_PASSWORD', usernameVariable: 'DOCKER_USERNAME')]) {
//                     docker.withRegistry('https://registry.hub.docker.com', 'docker-hub') {
//                     def dockerImage = docker.image('pet_innotter')
//
//                      // Логин в Docker Hub
//                     docker.login(username: X, password: X)
//
//                     // Загрузка образа в Docker Hub
//                     dockerImage.push()
//                 }
//               }
//             }
//           }
//         }
//
//
//     post {
//         always {
//             // Завершение и очистка контейнеров после выполнения пайплайна
//             script {
//                 def dockerComposeFile = './docker-compose.yml'
//
//                 // Остановка и удаление контейнеров
//                 sh "docker-compose -f ${dockerComposeFile} down"
//             }
//         }
//     }
// =======
  agent any

  stages {
    stage('Docker Login') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'dockerhubaccount', passwordVariable: 'DOCKER_PASSWORD', usernameVariable: 'DOCKER_USERNAME')]) {
          sh "docker login -u $DOCKER_USERNAME -p $DOCKER_PASSWORD"
        }
      }
    }

    stage('Build') {
      steps {
        sh 'sudo docker-compose build'
      }
    }

    stage('Rename') {
      steps {
        sh 'docker tag innotter-celery_worker:latest forartsake/celery_worker:latest'
        sh 'docker tag innotter-django_petproject:latest forartsake/django_petproject:latest'
      }
    }

    stage('Push') {
      steps {
        sh 'docker push forartsake/celery_worker:latest'
        sh 'docker push forartsake/django_petproject:latest'
      }
    }
  }
>>>>>>> 77d0254ce7f36d914360f3d444cad4a2e9370ae3
}
