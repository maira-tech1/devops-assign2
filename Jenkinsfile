pipeline {
    agent any

    tools {
        nodejs 'node18' 
    }

    environment {
        COMPOSE_PROJECT_NAME = "mern_ci_app"pipeline {
    agent any

    stages {
        stage('Checkout Code') {
            steps {
                echo 'Cloning repository...'
                checkout scm
            }
        }

        stage('Clean Previous Deployment') {
            steps {
                echo 'Stopping any previous CI deployment...'
                sh 'docker-compose -f docker-compose-ci.yml down --remove-orphans || true'
            }
        }

        stage('Build and Start') {
            steps {
                echo 'Starting containerized application...'
                sh 'docker-compose -f docker-compose-ci.yml up -d --build'
            }
        }

        stage('Health Check') {
            steps {
                echo 'Waiting for services to start...'
                sh 'sleep 30'
                sh 'docker-compose -f docker-compose-ci.yml ps'
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully! Application is up.'
        }
        failure {
            echo 'Pipeline failed!'
            sh 'docker-compose -f docker-compose-ci.yml down || true'
        }
    }
}
    }

    stages {

        stage('Checkout MERN App') {
            steps {
                echo 'Cloning MERN App...'
                
                checkout([
                    $class: 'GitSCM',
                    branches: [[name: '*/main']],
                    extensions: [
                        [$class: 'CloneOption', depth: 0, noTags: false, shallow: false]
                    ],
                    userRemoteConfigs: [[url: 'https://github.com/A5tab/E-Commerce-Docker-Container.git']]
                ])
                
                script {
                    // Force fetch full commit info
                    sh 'git fetch --unshallow || true'
                    
                    // Extract commit details with error handling
                    env.COMMIT_HASH = sh(
                        script: 'git rev-parse HEAD',
                        returnStdout: true
                    ).trim()
                    
                    env.COMMIT_EMAIL = sh(
                        script: 'git show -s --format="%ae" HEAD',
                        returnStdout: true
                    ).trim()
                    
                    env.COMMIT_AUTHOR = sh(
                        script: 'git show -s --format="%an" HEAD',
                        returnStdout: true
                    ).trim()
                    
                    env.COMMIT_MESSAGE = sh(
                        script: 'git show -s --format="%s" HEAD',
                        returnStdout: true
                    ).trim()
                    
                    // Debug output
                    echo "======================================="
                    echo "Commit Hash: ${env.COMMIT_HASH}"
                    echo "Commit Author: ${env.COMMIT_AUTHOR}"
                    echo "Commit Email: ${env.COMMIT_EMAIL}"
                    echo "Commit Message: ${env.COMMIT_MESSAGE}"
                    echo "======================================="
                    
                    // Validate
                    if (!env.COMMIT_EMAIL || env.COMMIT_EMAIL == 'null' || !env.COMMIT_EMAIL.contains('@')) {
                        echo "WARNING: Could not extract valid email!"
                        sh 'git log -1 --pretty=fuller'
                    }
                }
            }
        }

        stage('Check & Clean Docker') {
            steps {
                sh '''
                    echo "Docker Version:"
                    docker --version
                    docker compose version
                    docker ps -aq --filter "name=mern-" | xargs -r docker rm -f || true
                    docker compose down --volumes --remove-orphans || true
                    docker system prune -f || true
                '''
            }
        }

        stage('Build and Start') {
            steps {
                sh 'docker compose build'
                sh 'docker compose up -d'
            }
        }

        stage('Health Check') {
            steps {
                sh '''
                    echo "Checking backend..."
                    for i in {1..10}; do
                        curl -s http://localhost:4000 && echo "Backend is up!" && break
                        echo "Retry $i..."
                        sleep 5
                    done

                    echo "Checking frontend..."
                    for i in {1..10}; do
                        curl -s http://localhost:8085 && echo "Frontend is up!" && break
                        echo "Retry $i..."
                        sleep 5
                    done
                '''
            }
        }

        stage('Checkout Tests') {
            steps {
                dir('tests') { 
                    git branch: 'main', url: 'https://github.com/A5tab/MERN_Test.git'
                }
            }
        }

        stage('Run Tests') {
            steps {
                nodejs('node18') {
                    sh '''
                        cd tests
                        rm -rf node_modules package-lock.json
                        npm cache clean --force
                        npm install
                        npm test || true 
                    '''
                }
            }
        }

        stage('Archive Reports') {
            steps {
                script {
                    junit allowEmptyResults: true, testResults: 'tests/results.xml'
                }
            }
        }

    }

    post {
        always {
            script {
                // Get values with proper null checking
                def commitEmail = env.COMMIT_EMAIL ?: ''
                def commitAuthor = env.COMMIT_AUTHOR ?: 'Unknown'
                def commitHash = env.COMMIT_HASH ?: 'Unknown'
                def commitMessage = env.COMMIT_MESSAGE ?: 'No message'
                
                // Validate email
                def recipient = 'muhammadaftab584@gmail.com'
                if (commitEmail && commitEmail != 'null' && commitEmail.contains('@')) {
                    recipient = commitEmail
                    echo "Sending to committer: ${recipient}"
                } else {
                    echo "No valid committer email found. Using fallback: ${recipient}"
                }
                
                emailext (
                    to: recipient,
                    subject: "Build ${currentBuild.currentResult}: #${env.BUILD_NUMBER}",
                    body: """
Build Status: ${currentBuild.currentResult}
Build Number: ${env.BUILD_NUMBER}

Commit Details:
Author: ${commitAuthor}
Email: ${commitEmail ?: 'Not available'}
Hash: ${commitHash}
Message: ${commitMessage}


                    """
                )
            }
        }
    }

}
