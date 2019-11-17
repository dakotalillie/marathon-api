pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                checkout scm
                sh 'cp env/sample.dev.env .env'
                sh 'make start-ci -- -d --build'
                sleep(5)
            }
        }
        stage('Formatting') {
            steps {
                sh 'make black -- --check'
            }
        }
        stage('Lint') {
            steps {
                sh 'make lint'
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
