pipeline {
    agent any

    environment {
        // ── Docker Hub ────────────────────────────────────────────────────────
        // Store your Docker Hub username as a Jenkins Secret Text credential
        // with ID = DOCKER_HUB_USER
        DOCKER_HUB_USER    = credentials('DOCKER_HUB_USER')
        BACKEND_IMAGE      = "${DOCKER_HUB_USER}/rag-resume-backend"
        FRONTEND_IMAGE     = "${DOCKER_HUB_USER}/rag-resume-frontend"
        DOCKER_CREDENTIALS = 'dockerhub-credentials'

        // ── Deployment ────────────────────────────────────────────────────────
        DEPLOY_HOST        = credentials('DEPLOY_HOST')   // e.g. ubuntu@1.2.3.4
        SSH_CREDENTIALS    = 'deploy-ssh-key'
        DEPLOY_ENV_FILE    = credentials('backend-env-file')
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 45, unit: 'MINUTES')
        disableConcurrentBuilds()
    }

    stages {

        // ────────────────────────────────────────────────────────────────────
        // 1. CHECKOUT
        // ────────────────────────────────────────────────────────────────────
        stage('Checkout') {
            steps {
                checkout scm
                echo "Branch: ${env.GIT_BRANCH} | Commit: ${env.GIT_COMMIT}"
            }
        }

        // ────────────────────────────────────────────────────────────────────
        // 2. BACKEND — install dependencies and run tests
        //    All DB / LLM / embeddings are mocked — no external services needed
        // ────────────────────────────────────────────────────────────────────
        stage('Backend: Install & Test') {
            steps {
                dir('backend') {
                    sh '''
                        # Use python3 (available in the Jenkins container)
                        PYTHON=$(command -v python3.11 || command -v python3 || echo python3)
                        echo "Using Python: $PYTHON"
                        $PYTHON -m venv .venv
                        . .venv/bin/activate
                        pip install --upgrade pip --quiet
                        pip install -r requirements.txt --quiet
                    '''
                    sh '''
                        . .venv/bin/activate

                        # CI environment — no real MySQL, Ollama, or embeddings
                        export MYSQL_URL="sqlite+pysqlite:///:memory:"
                        export LLM_PROVIDER=ollama
                        export OLLAMA_URL=http://localhost:11434
                        export OLLAMA_MODEL=llama3:8b
                        export SECRET_KEY="ci-test-secret-key-32-chars-long!"
                        export ALGORITHM=HS256
                        export ACCESS_TOKEN_EXPIRE_MINUTES=1440
                        export OTP_EXPIRE_MINUTES=10
                        export CHROMA_PATH=/tmp/chroma_ci
                        export UPLOAD_PATH=/tmp/uploads_ci
                        export EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"
                        export CHUNK_SIZE=200
                        export CHUNK_OVERLAP=30
                        export TOP_K=5
                        export MAX_PDF_SIZE=10485760
                        export SMTP_HOST=localhost
                        export SMTP_PORT=25
                        export SMTP_USER=""
                        export SMTP_PASSWORD=""
                        export SMTP_FROM="noreply@ci.local"

                        pytest tests/ -v --tb=short --junitxml=test-results.xml
                    '''
                }
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'backend/test-results.xml'
                }
            }
        }

        // ────────────────────────────────────────────────────────────────────
        // 3. FRONTEND — install and build
        // ────────────────────────────────────────────────────────────────────
        stage('Frontend: Install & Build') {
            steps {
                dir('frontend') {
                    sh 'npm ci --prefer-offline'
                    sh 'npm run build'
                }
            }
        }

        // ────────────────────────────────────────────────────────────────────
        // 4. DOCKER — build images (main/master branch only)
        // ────────────────────────────────────────────────────────────────────
        stage('Docker: Build Images') {
            when {
                anyOf {
                    branch 'main'
                    branch 'master'
                    tag pattern: 'v\\d+\\.\\d+\\.\\d+', comparator: 'REGEXP'
                }
            }
            steps {
                script {
                    def tag = env.GIT_COMMIT.take(8)
                    sh "docker build -t ${BACKEND_IMAGE}:${tag} -t ${BACKEND_IMAGE}:latest backend/"
                    sh "docker build -t ${FRONTEND_IMAGE}:${tag} -t ${FRONTEND_IMAGE}:latest frontend/"
                }
            }
        }

        // ────────────────────────────────────────────────────────────────────
        // 5. DOCKER — push images to Docker Hub
        // ────────────────────────────────────────────────────────────────────
        stage('Docker: Push Images') {
            when {
                anyOf {
                    branch 'main'
                    branch 'master'
                    tag pattern: 'v\\d+\\.\\d+\\.\\d+', comparator: 'REGEXP'
                }
            }
            steps {
                script {
                    def tag = env.GIT_COMMIT.take(8)
                    withDockerRegistry(credentialsId: DOCKER_CREDENTIALS, url: 'https://index.docker.io/v1/') {
                        sh "docker push ${BACKEND_IMAGE}:${tag}"
                        sh "docker push ${BACKEND_IMAGE}:latest"
                        sh "docker push ${FRONTEND_IMAGE}:${tag}"
                        sh "docker push ${FRONTEND_IMAGE}:latest"
                    }
                }
            }
        }

        // ────────────────────────────────────────────────────────────────────
        // 6. DEPLOY — SSH to production server, pull and restart containers
        // ────────────────────────────────────────────────────────────────────
        stage('Deploy to Server') {
            when {
                anyOf {
                    branch 'main'
                    branch 'master'
                }
            }
            steps {
                script {
                    def tag = env.GIT_COMMIT.take(8)
                    sshagent(credentials: [SSH_CREDENTIALS]) {
                        sh """
                            # Upload the .env file to the server
                            scp -o StrictHostKeyChecking=no ${DEPLOY_ENV_FILE} ${DEPLOY_HOST}:~/rag-resume/.env

                            # Upload the production docker-compose file
                            scp -o StrictHostKeyChecking=no docker-compose.prod.yml ${DEPLOY_HOST}:~/rag-resume/docker-compose.yml

                            # Pull new images and restart
                            ssh -o StrictHostKeyChecking=no ${DEPLOY_HOST} \\
                                "cd ~/rag-resume && \\
                                 export BACKEND_IMAGE=${BACKEND_IMAGE}:${tag} && \\
                                 export FRONTEND_IMAGE=${FRONTEND_IMAGE}:${tag} && \\
                                 docker compose pull && \\
                                 docker compose up -d --remove-orphans && \\
                                 docker image prune -f"
                        """
                    }
                }
            }
        }
    }

    post {
        success {
            echo "✅ Build #${env.BUILD_NUMBER} passed on branch ${env.GIT_BRANCH}"
        }
        failure {
            echo "❌ Build #${env.BUILD_NUMBER} FAILED on branch ${env.GIT_BRANCH}"
            // Uncomment to send email on failure:
            // mail to: 'you@example.com',
            //      subject: "FAILED: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
            //      body: "Details: ${env.BUILD_URL}"
        }
        always {
            cleanWs()
        }
    }
}
