pipeline {
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
        sh 'docker tag db_postgresql:latest forartsake/db_postgresql:latest'
        sh 'docker tag django_petproject:latest forartsake/django_petproject:latest'
        sh 'docker tag rabbitmq:latest forartsake/rabbitmq:latest'
        sh 'docker tag celery_worker:latest forartsake/celery_worker:latest'
        sh 'docker tag celery_flower:latest forartsake/celery_flower:latest'
      }
    }

    stage('Push') {
      steps {
        sh 'docker push forartsake/db_postgresql:latest'
        sh 'docker push forartsake/django_petproject:latest'
        sh 'docker push forartsake/rabbitmq:latest'
        sh 'docker push forartsake/celery_worker:latest'
        sh 'docker push forartsake/celery_flower:latest'
      }
    }
  }
}
