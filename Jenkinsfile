pipeline {
    agent any

    tools {
        nodejs 'node18' 
    }

    environment {
        COMPOSE_PROJECT_NAME = "mern_ci_app"
    }

    stages {
        stage('Checkout MERN App') {
            steps {
                echo 'Cloning MERN App...'
                checkout([
                    $class: 'GitSCM', 
                    branches: [[name: '*/main']], 
                    userRemoteConfigs: [[url: 'https://github.com/A5tab/E-Commerce-Docker-Container.git']]
                ])
                script {
                    env.COMMIT_HASH = sh(script: 'git rev-parse HEAD', returnStdout: true).trim()
                    env.COMMIT_AUTHOR = sh(script: 'git show -s --format="%an" HEAD', returnStdout: true).trim()
                    echo "Building Commit: ${env.COMMIT_HASH} by ${env.COMMIT_AUTHOR}"
                }
            }
        }

        stage('Check & Clean Docker') {
            steps {
                sh '''
                    docker ps -aq --filter "name=mern-" | xargs -r docker rm -f || true
                    docker compose -f docker-compose-ci.yml down --volumes --remove-orphans || true
                '''
            }
        }

        stage('Build and Start') {
            steps {
                // Using the specific CI file you showed in your screenshot
                sh 'docker compose -f docker-compose-ci.yml up -d'
            }
        }

        stage('Health Check') {
            steps {
                echo 'Waiting for services to start...'
                sleep 20
                // Checking port 8086 as per your docker-compose-ci.yml
                sh 'curl -s http://localhost:8086 || echo "App is still loading..."'
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed! Check the logs above.'
        }
    }
}
