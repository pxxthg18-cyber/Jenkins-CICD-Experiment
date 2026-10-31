# Lab Experiment Report & Setup Manual

> **Experiment Title:**  
> *“Set up a CI/CD pipeline to automate the building, testing, and deployment of a containerized application.”*

---

## 1. System Environment & Inspection Results

| Component | Status | Details / Path |
| :--- | :--- | :--- |
| **Operating System** | Configured | Microsoft Windows 11 / x64 |
| **Java JDK** | **Java 21 LTS** | Eclipse Adoptium Temurin `21.0.13.9-hotspot`<br>`JAVA_HOME = C:\Users\preth\AppData\Local\Programs\Eclipse Adoptium\jdk-21.0.13.9-hotspot` |
| **Git Engine** | Installed | `git version 2.56.0.windows.2` |
| **Docker Desktop** | Active | `Docker version 29.9.2` (Linux engine on Windows WSL2 backend) |
| **Jenkins Server** | Active | Version `2.580.2` running at [http://localhost:8080](http://localhost:8080) |
| **Jenkins Docker Access** | Configured | Docker CLI (`26.1.5`) installed inside container with `/var/run/docker.sock` access |
| **Deployed Container** | Active | Container `flask-app-prod` running on [http://localhost:5000](http://localhost:5000) |

---

## 2. Project Architecture & Pipeline Structure

```text
Jenkins-CICD-Experiment/
├── app.py                  # Flask web service with '/' and '/health' endpoints
├── requirements.txt        # Flask==3.0.3, pytest==8.2.2, gunicorn==22.0.0
├── Dockerfile              # Containerization for 'jenkins-cicd-flask-app'
├── test_app.py             # 5 automated test cases executed via pytest
├── verify_deployment.py    # Post-deployment probe verifying live container health
├── Jenkinsfile             # 5-stage declarative Jenkins pipeline
├── .dockerignore           # Excludes git, pycache, venv from Docker build context
└── README.md               # Laboratory documentation and evaluation guide
```

---

## 3. Jenkins Declarative Pipeline Stages

The pipeline defines five automated stages in [Jenkinsfile](file:///c:/Users/preth/OneDrive/Desktop/Jenkins-CICD-Experiment/Jenkinsfile):

```text
┌─────────────────┐     ┌──────────────────────┐     ┌────────────────────────┐
│ 1. Checkout     │ ──> │ 2. Build Docker      │ ──> │ 3. Run Automated Tests │
│    Source Code  │     │    Image             │     │    (pytest in image)   │
└─────────────────┘     └──────────────────────┘     └────────────────────────┘
                                                                  │
                                                                  ▼
┌─────────────────┐     ┌──────────────────────┐
│ 5. Verify       │ <── │ 4. Deploy            │
│    Deployment   │     │    Application       │
└─────────────────┘     └──────────────────────┘
```

1. **Checkout:** Clones the repository revision matching the trigger.
2. **Build Docker Image:** Executes `docker build -t jenkins-cicd-flask-app:${BUILD_NUMBER} -t jenkins-cicd-flask-app:latest .`
3. **Run Automated Tests:** Runs `pytest test_app.py -v` *inside* the newly built Docker image. If any assertion fails, the command exits with code 1, immediately halting the pipeline before deployment.
4. **Deploy Application:** Stops and cleans up any existing `flask-app-prod` container, then spins up the new container with `--restart unless-stopped` on port 5000.
5. **Verify Deployment:** Executes `python3 verify_deployment.py 5000`, testing the live container's `/health` endpoint to ensure HTTP 200 before marking the build as `SUCCESS`.

---

## 4. Live Verification Output

### Actual Jenkins Console Output (Build #6 — Status: SUCCESS)
```text
[Pipeline] stage: Checkout
Checking out Revision 9d95a50...
Commit message: "Add verify_deployment.py script and update Stage 5 in Jenkinsfile"

[Pipeline] stage: Build Docker Image
===> [Stage 2/5] Building Docker image: jenkins-cicd-flask-app:6...
+ docker build -t jenkins-cicd-flask-app:6 -t jenkins-cicd-flask-app:latest .

[Pipeline] stage: Run Automated Tests
===> [Stage 3/5] Executing pytest test suite inside container...
+ docker run --rm jenkins-cicd-flask-app:6 pytest test_app.py -v
============================= test session starts ==============================
collected 5 items
test_app.py::test_home_page_status_code PASSED                           [ 20%]
test_app.py::test_home_page_content PASSED                               [ 40%]
test_app.py::test_health_endpoint_status PASSED                          [ 60%]
test_app.py::test_health_endpoint_json_payload PASSED                    [ 80%]
test_app.py::test_invalid_route_returns_404 PASSED                       [100%]
============================== 5 passed in 0.14s ===============================

[Pipeline] stage: Deploy Application
===> [Stage 4/5] Deploying containerized application...
Starting container 'flask-app-prod' on port 5000...
+ docker run -d --name flask-app-prod --restart unless-stopped -p 5000:5000 jenkins-cicd-flask-app:6

[Pipeline] stage: Verify Deployment
===> [Stage 5/5] Verifying application deployment health...
Waiting for container initialization...
Checking deployment health at http://host.docker.internal:5000/health...
SUCCESS: Health check verified on http://host.docker.internal:5000/health!
Payload: {'app': 'jenkins-cicd-flask-app', 'status': 'healthy', 'version': '1.0.1'}

[Pipeline] echo
=================================================================
CI/CD Pipeline Completed Successfully!
Application is live at: http://localhost:5000
Health endpoint: http://localhost:5000/health
=================================================================
Finished: SUCCESS
```

---

## 5. How to Connect to Your Remote GitHub Repository

To demonstrate automated webhooks and Git triggers with your personal GitHub account:

### Step 5.1: Create a GitHub Repository
1. Go to [github.com/new](https://github.com/new) and create a repository named `Jenkins-CICD-Experiment`.
2. Add your GitHub remote in PowerShell:
   ```powershell
   git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/Jenkins-CICD-Experiment.git
   git push -u origin main
   ```

### Step 5.2: Update the Jenkins Job Git SCM URL
1. Open Jenkins at [http://localhost:8080/job/flask-cicd-pipeline/configure](http://localhost:8080/job/flask-cicd-pipeline/configure).
2. Under **Pipeline** &rarr; **Repository URL**, replace the internal path with:
   `https://github.com/<YOUR_GITHUB_USERNAME>/Jenkins-CICD-Experiment.git`
3. If the repository is private, select your GitHub Personal Access Token under **Credentials**.
4. Click **Save**.

### Step 5.3: Automated Trigger via SCM Polling / Webhook
- **SCM Polling (Built-in):** Jenkins polls GitHub every 2 minutes (`H/2 * * * *`). Any push to `main` automatically triggers a build.
- **GitHub Webhook (Instant Trigger):**
  1. In your GitHub repository, go to **Settings** &rarr; **Webhooks** &rarr; **Add webhook**.
  2. Set Payload URL: `http://<your-public-ip-or-ngrok>:8080/github-webhook/`
  3. Content type: `application/json`
  4. Trigger: *Just the push event*.

---

## 6. Accessing Your Deployed Application & Jenkins Dashboard

- **Jenkins Pipeline GUI:** [http://localhost:8080/job/flask-cicd-pipeline/](http://localhost:8080/job/flask-cicd-pipeline/)
- **Live Flask Application UI:** [http://localhost:5000](http://localhost:5000)
- **Live Health Status Endpoint:** [http://localhost:5000/health](http://localhost:5000/health)
