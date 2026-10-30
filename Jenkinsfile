pipeline {
    agent any

    environment {
        // ── Docker Hub ────────────────────────────────────────────────────────
        DOCKER_HUB_USER    = credentials('DOCKER_HUB_USER')
        BACKEND_IMAGE      = "${DOCKER_HUB_USER}/rag-resume-backend"
        FRONTEND_IMAGE     = "${DOCKER_HUB_USER}/rag-resume-frontend"
        DOCKER_CREDENTIALS = 'dockerhub-credentials'
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 45, unit: 'MINUTES')
        disableConcurrentBuilds()
    }

    stages {

        // ── 1. CHECKOUT ───────────────────────────────────────────────────────
        stage('Checkout') {
            steps {
                checkout scm
                echo "Branch: ${env.GIT_BRANCH} | Commit: ${env.GIT_COMMIT}"
            }
        }

        // ── 2. BACKEND TESTS ──────────────────────────────────────────────────
        stage('Backend: Install & Test') {
            steps {
                dir('backend') {
                    sh '''
                        python3 -m venv .venv
                        . .venv/bin/activate
                        pip install --upgrade pip --quiet
                        pip install -r requirements.txt --quiet
                    '''
                    sh '''
                        . .venv/bin/activate
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

        // ── 3. FRONTEND BUILD ─────────────────────────────────────────────────
        stage('Frontend: Install & Build') {
            steps {
                dir('frontend') {
                    sh 'npm ci --prefer-offline'
                    sh 'npm run build'
                }
            }
        }

        // ── 4. DOCKER BUILD ───────────────────────────────────────────────────
        stage('Docker: Build Images') {
            when {
                anyOf { branch 'master'; branch 'main' }
            }
            steps {
                script {
                    def tag = env.GIT_COMMIT.take(8)
                    sh "docker build -t ${BACKEND_IMAGE}:${tag} -t ${BACKEND_IMAGE}:latest backend/"
                    sh "docker build -t ${FRONTEND_IMAGE}:${tag} -t ${FRONTEND_IMAGE}:latest frontend/"
                }
            }
        }

        // ── 5. DOCKER PUSH ────────────────────────────────────────────────────
        stage('Docker: Push Images') {
            when {
                anyOf { branch 'master'; branch 'main' }
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
    }

    post {
        success {
            echo "✅ Build #${env.BUILD_NUMBER} passed — ${env.GIT_BRANCH}"
        }
        failure {
            echo "❌ Build #${env.BUILD_NUMBER} FAILED — ${env.GIT_BRANCH}"
        }
        always {
            node('built-in') {
                cleanWs()
            }
        }
    }
}
