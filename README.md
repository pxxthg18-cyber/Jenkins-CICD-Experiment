# Experiment: Automated CI/CD Pipeline for a Containerized Application

> **College Lab Experiment Title:**  
> *“Set up a CI/CD pipeline to automate the building, testing, and deployment of a containerized application.”*

---

## 1. Overview & Objectives

In modern DevOps practices, **Continuous Integration (CI)** and **Continuous Deployment (CD)** allow developers to automatically validate code changes, run automated tests, package software into immutable container images, and deploy them with minimal human intervention.

### Experiment Objectives:
1. Develop a lightweight web service with a status endpoint using **Python & Flask**.
2. Write automated unit tests using **pytest**.
3. Package the application as an isolated container image using **Docker** (`jenkins-cicd-flask-app`).
4. Automate the end-to-end workflow using a **declarative Jenkins pipeline** (`Jenkinsfile`):
   - **Checkout:** Pull source code from Git.
   - **Build:** Create the Docker container image.
   - **Test:** Run automated unit tests inside the container.
   - **Deploy:** Deploy the containerized application using configurable target environments.

---

## 2. Project File Structure

```text
Jenkins-CICD-Experiment/
├── app.py              # Flask web application with '/' and '/health' endpoints
├── requirements.txt    # Application and testing dependencies (Flask, pytest, gunicorn)
├── Dockerfile          # Instructions to build 'jenkins-cicd-flask-app' image
├── test_app.py         # Automated unit tests evaluated via pytest
├── Jenkinsfile         # Declarative 4-stage Jenkins CI/CD pipeline
├── .dockerignore       # Specifies files excluded from Docker build context
└── README.md           # Documentation, lab setup instructions, and viva preparation
```

---

## 3. Prerequisites

Ensure the following tools are installed on your workstation or lab server:

| Tool | Version | Purpose |
| :--- | :--- | :--- |
| **Python** | 3.10+ | Local development and test verification |
| **Git** | 2.x+ | Source code version control |
| **Docker** | 20.x+ | Container engine to build and run container images |
| **Jenkins** | 2.400+ | Automation server to orchestrate the CI/CD pipeline |

---

## 4. Running the Application Locally (Without Jenkins)

Before configuring Jenkins, it is recommended to test each component individually.

### Step 4.1: Clone or Open the Repository
```bash
cd Jenkins-CICD-Experiment
```

### Step 4.2: Create a Virtual Environment & Install Dependencies
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On Linux / macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 4.3: Run Automated Unit Tests
```bash
python -m pytest test_app.py -v
```
*Expected Output:* 5 tests passing (`PASSED [100%]`).

### Step 4.4: Run the Flask Web Application
```bash
python app.py
```
Open your browser and navigate to:
- **Home UI:** `http://localhost:5000`
- **Health Check API:** `http://localhost:5000/health` (Returns `{"status": "healthy", "app": "jenkins-cicd-flask-app", "version": "1.0.0"}`)

---

## 5. Containerizing with Docker

### Step 5.1: Build the Docker Image
Build the container image using the specified name `jenkins-cicd-flask-app`:
```bash
docker build -t jenkins-cicd-flask-app:latest .
```

### Step 5.2: Test Inside the Container
Verify that automated tests pass inside the container environment:
```bash
docker run --rm jenkins-cicd-flask-app:latest pytest test_app.py -v
```

### Step 5.3: Run the Container
```bash
docker run -d --name flask-app-test -p 5000:5000 jenkins-cicd-flask-app:latest
```
Verify the container is running:
```bash
docker ps
curl http://localhost:5000/health
```

Stop and clean up:
```bash
docker stop flask-app-test
docker rm flask-app-test
```

---

## 6. Jenkins CI/CD Pipeline Setup

### Step 6.1: Required Jenkins Plugins
In Jenkins, navigate to **Manage Jenkins** &rarr; **Plugins** &rarr; **Available Plugins**, and install:
1. **Pipeline** (Workflow Aggregator)
2. **Git Plugin**
3. **Docker Pipeline** / **Docker Plugin**
4. **Credentials Binding Plugin**

### Step 6.2: Ensure Jenkins Has Docker Execution Permissions
If Jenkins runs on a Linux host, grant the `jenkins` system user access to the Docker daemon socket:
```bash
sudo usermod -aG docker jenkins
sudo systemctl restart jenkins
```

### Step 6.3: Create the Pipeline Job in Jenkins
1. Click **New Item** on the Jenkins dashboard.
2. Enter item name: `flask-cicd-pipeline`.
3. Select **Pipeline** and click **OK**.
4. Scroll to the **Pipeline** section:
   - **Definition:** Select *Pipeline script from SCM*.
   - **SCM:** Select *Git*.
   - **Repository URL:** Enter your Git repository URL (e.g., GitHub or local Git repo).
   - **Branch Specifier:** `*/main` (or `*/master`).
   - **Script Path:** `Jenkinsfile`.
5. Click **Save**.

### Step 6.4: Run the Pipeline
1. Click **Build with Parameters** (or **Build Now** for the first run so Jenkins reads parameters).
2. Choose your deployment strategy:
   - `local_container`: (Recommended for college labs) Spins up the container directly on port 5000 of the Jenkins host.
   - `docker_hub`: Pushes the image to Docker Hub registry.
   - `cloud_vm_or_cluster`: Deploys to a remote VM or cloud cluster.
3. Click **Build**.
4. Monitor the stage view as stages complete:
   - `Checkout Source Code` &rarr; `Build Docker Image` &rarr; `Run Automated Tests` &rarr; `Deploy Containerized Application`.

---

## 7. Deployment Configuration & Cloud Credentials Guide

The deployment stage in `Jenkinsfile` is configurable. Here is what is required for each deployment mode:

### 1. Local Container Deployment (`local_container`)
- **Use Case:** College lab evaluation and local demonstration.
- **Requirements:** Docker daemon running on the Jenkins agent.
- **Credentials Required:** None (uses local Docker socket).
- **Result:** Stops any existing `flask-app-prod` container and launches the new build on `http://localhost:5000`.

### 2. Docker Hub Registry Deployment (`docker_hub`)
- **Use Case:** Storing versioned images in a central registry for remote servers to pull.
- **Credentials Setup in Jenkins:**
  1. Navigate to **Manage Jenkins** &rarr; **Credentials** &rarr; **System** &rarr; **Global credentials**.
  2. Click **Add Credentials**:
     - **Kind:** *Username with password*
     - **Scope:** *Global*
     - **Username:** Your Docker Hub username
     - **Password:** Your Docker Hub Personal Access Token (PAT)
     - **ID:** `docker-hub-credentials` (matches `DOCKER_CREDENTIALS_ID` in `Jenkinsfile`)
  3. Enter your Docker Hub username in the build parameter `DOCKER_REGISTRY_USER`.

### 3. Cloud Deployment (`cloud_vm_or_cluster`)
- **Use Case:** Production deployments to AWS, Azure, Google Cloud Platform (GCP), or a remote Linux VPS.
- **Required Cloud Configuration & Credentials:**
  - **AWS (EC2 / ECS / EKS):**
    - Install AWS CLI on the Jenkins agent.
    - Add AWS Access Key ID and Secret Access Key to Jenkins Credentials with ID `aws-cloud-credentials`.
    - Configure IAM policies granting permissions to Amazon ECR (`ecr:GetAuthorizationToken`, `ecr:PutImage`) and ECS/EKS.
  - **Remote Linux VM via SSH:**
    - Generate an SSH keypair (`ssh-keygen`).
    - Add the private key to Jenkins Credentials as **SSH Username with private key** with ID `cloud-server-ssh-key`.
    - Install public key on target VM in `~/.ssh/authorized_keys`.
    - Deployment script executes:
      ```bash
      ssh -o StrictHostKeyChecking=no user@cloud-ip \
        "docker pull ${REGISTRY_USER}/jenkins-cicd-flask-app:latest && \
         docker stop flask-app || true && \
         docker run -d --name flask-app -p 80:5000 ${REGISTRY_USER}/jenkins-cicd-flask-app:latest"
      ```

---

## 8. College Lab Viva / Oral Exam Questions & Answers

<details>
<summary><strong>Q1: What is the difference between Continuous Integration (CI) and Continuous Deployment (CD)?</strong></summary>
<blockquote>
<strong>CI (Continuous Integration):</strong> Automatically merges developer code into a shared repository, builds the application, and runs automated tests (pytest) to catch integration errors early.<br>
<strong>CD (Continuous Deployment):</strong> Automatically packages the tested build into a production-ready artifact (Docker image) and deploys it directly to target environments without manual intervention.
</blockquote>
</details>

<details>
<summary><strong>Q2: Why run unit tests inside the Docker container rather than on the Jenkins host?</strong></summary>
<blockquote>
Running tests inside the built container ensures parity between the test environment and the production environment. It verifies that Python dependencies, system libraries, and file paths inside the image work exactly as expected.
</blockquote>
</details>

<details>
<summary><strong>Q3: What is the purpose of the <code>/health</code> endpoint?</strong></summary>
<blockquote>
The health check endpoint provides a lightweight, automated probe used by Docker's <code>HEALTHCHECK</code> instruction, Kubernetes liveness/readiness probes, and load balancers to determine whether the web application is running and responding to requests.
</blockquote>
</details>

<details>
<summary><strong>Q4: Why use <code>.dockerignore</code>?</strong></summary>
<blockquote>
<code>.dockerignore</code> excludes unnecessary files (such as <code>.git</code>, virtual environments <code>venv/</code>, test caches, and documentation) from being sent to the Docker daemon. This reduces image size, accelerates build times, and prevents sensitive files from leaking into the container.
</blockquote>
</details>

<details>
<summary><strong>Q5: How does Jenkins securely handle secrets like Docker Hub or Cloud credentials?</strong></summary>
<blockquote>
Jenkins uses its built-in Credentials Store. Secrets are encrypted on disk and injected into pipelines as masked environment variables using the <code>withCredentials</code> block. They are never hardcoded in scripts or exposed in console logs.
</blockquote>
</details>
