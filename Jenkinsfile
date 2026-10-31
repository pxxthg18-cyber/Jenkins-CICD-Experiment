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
            description: 'Target environment: local container or cloud platform'
        )
        string(
            name: 'APP_PORT',
            defaultValue: '5000',
            description: 'Port mapped to host for accessing the Flask service'
        )
    }

    environment {
        IMAGE_NAME     = 'jenkins-cicd-flask-app'
        IMAGE_TAG      = "${BUILD_NUMBER}"
        CONTAINER_NAME = 'flask-app-prod'
        HOST_PORT      = "${params.APP_PORT}"

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
                echo "===> [Stage 1/5] Checking out source code from Git repository..."
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
                /*
                 * Tests are executed inside the built container image.
                 * If any pytest assertion fails, the command exits with non-zero,
                 * immediately terminating the pipeline and preventing deployment.
                 */
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
                echo "===> [Stage 4/5] Deploying containerized application to ${params.DEPLOY_ENV} environment..."
                script {
                    if (params.DEPLOY_ENV == 'local') {
                        sh """
                            # Stop & remove any running production container
                            if [ \$(docker ps -a -q -f name=^/${CONTAINER_NAME}\$) ]; then
                                echo "Removing existing container '${CONTAINER_NAME}'..."
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
                    } else if (params.DEPLOY_ENV == 'cloud') {
                        echo "Cloud deployment target selected."
                        /*
                         * Cloud Deployment Pattern (e.g. AWS ECS / Cloud Run / Kubernetes):
                         * In production, withCredentials wraps the cloud CLI or Docker push commands:
                         *
                         * withCredentials([usernamePassword(credentialsId: env.DOCKER_HUB_CREDS_ID, ...)]) {
                         *     sh 'docker login -u $USER -p $PASS && docker push $IMAGE'
                         * }
                         */
                        echo "Cloud credentials required: configure '${env.AWS_CREDS_ID}' in Jenkins Credentials."
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
                    if (params.DEPLOY_ENV == 'local') {
                        sh """
                            echo "Waiting for container initialization..."
                            sleep 3

                            # Verify container status is running
                            docker ps -f name=${CONTAINER_NAME}

                            # Verify the /health endpoint responds with HTTP 200
                            # Using python urllib inside Jenkins to avoid curl dependency
                            python3 -c "import urllib.request, json; \
                                res = urllib.request.urlopen('http://localhost:${HOST_PORT}/health'); \
                                data = json.loads(res.read().decode()); \
                                assert res.status == 200, f'Expected 200 but got {res.status}'; \
                                assert data.get('status') == 'healthy', 'Health check status is not healthy'; \
                                print('Deployment verification passed! Endpoint output:', data)"
                        """
                    } else {
                        echo "Cloud verification: ping remote health endpoint when configured."
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
            echo "Pipeline run finished."
        }
    }
}
