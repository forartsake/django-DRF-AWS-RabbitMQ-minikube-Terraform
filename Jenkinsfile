pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                script {
                    // Проверка билда контейнеров
                    docker.withRegistry('') {
                        def dockerCompose = dockerComposeFile()
                        dockerCompose.build()
                    }
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    // Запуск pytest на машине
                    sh 'pytest'
                }
            }
        }
    }
}
