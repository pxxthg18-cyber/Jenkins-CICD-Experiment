pipeline {
    /*
     * Jenkins Declarative Pipeline
     * Experiment: Automated CI/CD Pipeline for Containerized Application
     * Image Name: jenkins-cicd-flask-app
     */
    agent any

    parameters {
        choice(
            name: 'DEPLOY_ENV',
            choices: ['local', 'cloud'],
            description: 'Target deployment environment'
        )
        string(
            name: 'APP_PORT',
            defaultValue: '5000',
            description: 'Host port for application access'
        )
    }

    environment {
        IMAGE_NAME     = 'jenkins-cicd-flask-app'
        IMAGE_TAG      = "${BUILD_NUMBER}"
        CONTAINER_NAME = 'flask-app-prod'
        TARGET_ENV     = "${params.DEPLOY_ENV ?: 'local'}"
        HOST_PORT      = "${params.APP_PORT ?: '5000'}"

        /*
         * Credentials configured under: Jenkins -> Manage Jenkins -> Credentials
         */
        DOCKER_HUB_CREDS_ID = 'docker-hub-credentials'
        AWS_CREDS_ID        = 'aws-cloud-credentials'
    }

    options {
        timeout(time: 15, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timestamps()
    }

    stages {
        // =====================================================================
        // STAGE 1: Checkout
        // =====================================================================
        stage('Checkout') {
            steps {
                echo "===> [Stage 1/5] Checking out source code..."
                checkout scm
            }
        }

        // =====================================================================
        // STAGE 2: Build Docker Image
        // =====================================================================
        stage('Build Docker Image') {
            steps {
                echo "===> [Stage 2/5] Building Docker image: ${IMAGE_NAME}:${IMAGE_TAG}..."
                sh """
                    docker build \
                        -t ${IMAGE_NAME}:${IMAGE_TAG} \
                        -t ${IMAGE_NAME}:latest .
                """
            }
        }

        // =====================================================================
        // STAGE 3: Run Automated Tests
        // =====================================================================
        stage('Run Automated Tests') {
            steps {
                echo "===> [Stage 3/5] Executing pytest test suite inside container..."
                sh """
                    docker run --rm ${IMAGE_NAME}:${IMAGE_TAG} pytest test_app.py -v
                """
            }
        }

        // =====================================================================
        // STAGE 4: Deploy Application
        // =====================================================================
        stage('Deploy Application') {
            steps {
                echo "===> [Stage 4/5] Deploying containerized application..."
                script {
                    if (env.TARGET_ENV == 'local') {
                        sh """
                            # Stop and remove any prior container
                            if [ \$(docker ps -a -q -f name=^/${CONTAINER_NAME}\$) ]; then
                                echo "Removing pre-existing container '${CONTAINER_NAME}'..."
                                docker stop ${CONTAINER_NAME} || true
                                docker rm ${CONTAINER_NAME} || true
                            fi

                            # Launch newly built container
                            echo "Starting container '${CONTAINER_NAME}' on port ${HOST_PORT}..."
                            docker run -d \
                                --name ${CONTAINER_NAME} \
                                --restart unless-stopped \
                                -p ${HOST_PORT}:5000 \
                                ${IMAGE_NAME}:${IMAGE_TAG}
                        """
                    } else {
                        echo "Cloud deployment target selected. Configure '${env.AWS_CREDS_ID}' in Jenkins."
                    }
                }
            }
        }

        // =====================================================================
        // STAGE 5: Verify Deployment
        // =====================================================================
        stage('Verify Deployment') {
            steps {
                echo "===> [Stage 5/5] Verifying application deployment health..."
                script {
                    if (env.TARGET_ENV == 'local') {
                        sh """
                            echo "Waiting for container initialization..."
                            sleep 3

                            # Verify container status
                            docker ps -f name=${CONTAINER_NAME}

                            # Verify the /health endpoint returns HTTP 200 using python urllib
                            python3 -c "import urllib.request, json; \
                                urls = ['http://host.docker.internal:${HOST_PORT}/health', 'http://localhost:${HOST_PORT}/health']; \
                                data = None; \
                                for u in urls: \
                                    try: \
                                        res = urllib.request.urlopen(u, timeout=5); \
                                        if res.status == 200: \
                                            data = json.loads(res.read().decode()); \
                                            print(f'Deployment verification passed on {u}! Output:', data); \
                                            break; \
                                    except Exception as e: \
                                        pass; \
                                assert data is not None and data.get('status') == 'healthy', 'Health check failed on all URLs'"
                        """
                    } else {
                        echo "Cloud verification: ping remote health endpoint."
                    }
                }
            }
        }
    }

    // =========================================================================
    // POST ACTIONS
    // =========================================================================
    post {
        success {
            echo "================================================================="
            echo "CI/CD Pipeline Completed Successfully!"
            echo "Application is live at: http://localhost:${HOST_PORT}"
            echo "Health endpoint: http://localhost:${HOST_PORT}/health"
            echo "================================================================="
        }
        failure {
            echo "================================================================="
            echo "Pipeline Failed! Deployment aborted or tests failed."
            echo "================================================================="
        }
        always {
            echo "Pipeline execution finished."
        }
    }
}
