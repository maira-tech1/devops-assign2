pipeline {
    agent any

    environment {
        COMPOSE_PROJECT_NAME = "mern_ci_app"
        REPO_URL = "https://github.com/maira-tech1/devops-assign2.git"
    }

    stages {

        stage('Checkout') {
            steps {
                echo 'Cloning repository from GitHub...'
                git branch: 'main', url: "${REPO_URL}"
            }
        }

        stage('Clean Previous Containers') {
            steps {
                echo 'Stopping and removing any previous CI containers...'
                sh '''
                    docker compose -f docker-compose-ci.yml down --remove-orphans || true
                    docker ps -aq --filter "name=mern-.*-ci" | xargs -r docker rm -f || true
                '''
            }
        }

        stage('Build and Start') {
            steps {
                echo 'Building and launching containerized MERN app...'
                sh 'docker compose -f docker-compose-ci.yml up -d'
            }
        }

        stage('Health Check') {
            steps {
                echo 'Waiting for services to initialize...'
                sleep(time: 20, unit: 'SECONDS')
                sh 'docker ps --filter "name=mern-.*-ci"'
                sh 'docker compose -f docker-compose-ci.yml logs --tail=20 backend-ci || true'
            }
        }

    }

    post {
        success {
            echo 'Pipeline completed! MERN app is up on ports 4001 (backend) and 8086 (frontend).'
        }
        failure {
            echo 'Pipeline failed. Check logs above.'
            sh 'docker compose -f docker-compose-ci.yml logs --tail=50 || true'
        }
    }
}
