pipeline {
    agent any



    environment {
        COMPOSE_PROJECT_NAME = "mern_ci_app"
        APP_URL              = "http://localhost:8086"
        TEST_IMAGE           = "selenium-tests:latest"
    }

    // ─────────────────────────────────────────────
    // Trigger on every GitHub push (requires the
    // GitHub plugin + webhook configured in GitHub)
    // ─────────────────────────────────────────────
    triggers {
        githubPush()
    }

    stages {

        // ── 1. Checkout test repo (this repo) ────
        stage('Checkout') {
            steps {
                echo 'Checking out test repository...'
                checkout scm
            }
        }

        // ── 2. Checkout the MERN Application ─────
        stage('Checkout MERN App') {
            steps {
                echo 'Cloning MERN Application...'
                dir('app') {
                    checkout([
                        $class           : 'GitSCM',
                        branches         : [[name: '*/main']],
                        userRemoteConfigs: [[url: 'https://github.com/A5tab/E-Commerce-Docker-Container.git']]
                    ])
                }
            }
        }

        // ── 3. Clean up any leftover containers ──
        stage('Clean Docker') {
            steps {
                sh '''
                    docker ps -aq --filter "name=mern-" | xargs -r docker rm -f || true
                    docker compose -f docker-compose-ci.yml down --volumes --remove-orphans || true
                '''
            }
        }

        // ── 4. Build & Start the MERN App ────────
        stage('Build and Start App') {
            steps {
                echo 'Starting MERN application in CI mode...'
                sh 'docker compose -f docker-compose-ci.yml up -d'
            }
        }

        // ── 5. Health Check ───────────────────────
        stage('Health Check') {
            steps {
                echo 'Waiting 30s for services to be ready...'
                sleep 30
                sh '''
                    echo "Checking frontend on port 8086..."
                    curl -sf http://localhost:8086 > /dev/null && echo "Frontend OK" || echo "Frontend still loading"
                    echo "Checking backend on port 4001..."
                    curl -sf http://localhost:4001/api/v1/healthcheck > /dev/null && echo "Backend OK" || echo "Backend check done"
                '''
            }
        }

        // ── 6. BUILD TEST DOCKER IMAGE ────────────
        stage('Build Test Image') {
            steps {
                echo 'Building Selenium test Docker image...'
                dir('tests') {
                    sh "docker build -t ${TEST_IMAGE} ."
                }
            }
        }

        // ── 7. RUN SELENIUM TESTS ─────────────────
        stage('Run Selenium Tests') {
            steps {
                echo 'Running 15 Selenium test cases in containerized Chrome...'
                sh '''
                    docker run --rm \
                        --network host \
                        -e APP_URL=${APP_URL} \
                        -v $(pwd)/tests/test-results:/tests/test-results \
                        ${TEST_IMAGE} \
                        python -m pytest test_ecommerce.py \
                            -v \
                            --tb=short \
                            --junit-xml=test-results/results.xml \
                            2>&1 | tee tests/test-output.txt
                '''
            }
            post {
                always {
                    // Publish JUnit XML results so Jenkins shows pass/fail per test
                    junit allowEmptyResults: true, testResults: 'tests/test-results/results.xml'
                }
            }
        }

        // ── 8. Bring down containers after tests ─
        stage('Teardown') {
            steps {
                echo 'Tearing down CI deployment...'
                sh 'docker compose -f docker-compose-ci.yml down --volumes --remove-orphans || true'
            }
        }
    }

    // ─────────────────────────────────────────────
    // Post-build: Email test results to the pusher
    // Requires: Email Extension Plugin in Jenkins
    //           + SMTP configured under Manage Jenkins
    // ─────────────────────────────────────────────
    post {
        always {
            script {
                // Capture who pushed (requires Git plugin)
                def pusherEmail = ''
                try {
                    pusherEmail = sh(
                        script: "git log -1 --pretty=format:'%ae'",
                        returnStdout: true
                    ).trim()
                } catch (Exception e) {
                    pusherEmail = 'devops-team@example.com'
                    echo "Could not determine pusher email, using default: ${pusherEmail}"
                }

                def testOutput = ''
                try {
                    testOutput = readFile('tests/test-output.txt')
                } catch (Exception e) {
                    testOutput = 'Test output not available.'
                }

                def subject = "[Jenkins] ${currentBuild.result ?: 'UNKNOWN'} - Build #${BUILD_NUMBER} - ${env.JOB_NAME}"
                def body = """
<html>
<body>
<h2>Jenkins Pipeline - Test Results</h2>
<table border="1" cellpadding="6" cellspacing="0">
  <tr><td><b>Job</b></td><td>${env.JOB_NAME}</td></tr>
  <tr><td><b>Build #</b></td><td>${BUILD_NUMBER}</td></tr>
  <tr><td><b>Status</b></td><td>${currentBuild.result ?: 'IN PROGRESS'}</td></tr>
  <tr><td><b>Duration</b></td><td>${currentBuild.durationString}</td></tr>
  <tr><td><b>Triggered by push from</b></td><td>${pusherEmail}</td></tr>
  <tr><td><b>Build URL</b></td><td><a href="${BUILD_URL}">${BUILD_URL}</a></td></tr>
</table>

<h3>Selenium Test Output</h3>
<pre style="background:#f4f4f4;padding:10px;border:1px solid #ccc;overflow:auto;">
${testOutput.take(8000)}
</pre>

<p>Full test report available at: <a href="${BUILD_URL}testReport">${BUILD_URL}testReport</a></p>
</body>
</html>
"""

                emailext(
                    to           : "mairamalyk13@gmail.com",
                    subject      : subject,
                    body         : body,
                    mimeType     : 'text/html',
                    attachmentsPattern: 'tests/test-results/results.xml'
                )
                echo "Test results emailed ONLY to you"
            }
        }

        success {
            echo 'Pipeline PASSED - All stages completed successfully!'
        }

        failure {
            echo 'Pipeline FAILED - Check the logs and test report above.'
        }
    }
}
