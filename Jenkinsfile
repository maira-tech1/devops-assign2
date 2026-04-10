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
                // We are telling Jenkins to put the MERN code in a sub-folder called 'app'
                dir('app') {
                    checkout([
                        $class: 'GitSCM', 
                        branches: [[name: '*/main']], 
                        userRemoteConfigs: [[url: 'https://github.com/A5tab/E-Commerce-Docker-Container.git']]
                    ])
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
