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
                    docker compose down --volumes --remove-orphans || true
                '''
            }
        }

      stage('Build and Start') {
            steps {
                // We use -f to specify the exact CI filename
                sh 'docker compose -f docker-compose-ci.yml up -d'
            }
        }

        stage('Health Check') {
            steps {
                sh '''
                    echo "Checking backend..."
                    sleep 10
                    curl -s http://localhost:4000 || echo "Backend not ready yet"
                '''
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}
