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
}
