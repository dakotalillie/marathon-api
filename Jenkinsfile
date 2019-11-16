pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                checkout scm
                sh 'cp env/sample.dev.env .env'
                sh 'make start-ci -- -d --build'
            }
        }
        stage('Test') {
            steps {
                sh 'make tests'
            }
        }
    }
    post {
        always {
            sh 'make stop-ci'
            cleanWs()
        }
    }
}
