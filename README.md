# DevOps Project Report: End-to-End DevOps CI/CD Pipeline for a Flask Application

# Project Overview

This project demonstrates how to implement a complete Continuous Integration and Continuous Deployment (CI/CD) pipeline for a Flask web application.

The pipeline automates the entire software delivery lifecycle—from source code management to deployment—ensuring faster, reliable, and consistent application releases.

The pipeline automatically:

- Clones the source code from GitHub
- Performs static code analysis using SonarQube
- Quality Gate validation
- Builds a Docker image
- Pushes the Docker image to Docker Hub
- Deploys the application using Docker Compose
- Connects the application with a MySQL database


# Technologies Used
| Technology           | Purpose                    |
| -------------------- | -------------------------- |
| Python               | Backend Development        |
| Flask                | Web Framework              |
| MySQL                | Database                   |
| Git                  | Version Control            |
| GitHub               | Source Code Repository     |
| Jenkins              | CI/CD Automation           |
| SonarQube            | Static Code Analysis       |
| Docker               | Containerization           |
| Docker Hub           | Image Repository           |
| Docker Compose       | Multi-container Deployment |
| Linux (Amazon Linux) | Deployment Environment     |


# Project Structure
```text

Automated-CICD-Pipeline-for-Containerized-Flask-Application
│
├── app.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── Jenkinsfile
├── templates/
│   ├── login.html
│   ├── register.html
│   └── dashboard.html
├── static/
├── database/
│   └── init.sql
└── README.md
```

# Install the following software before running the project:

- Python 3.x
- Git
- Docker
- Docker Compose
- Jenkins
- SonarQube Server
- Docker Hub Account

# Step 1: AWS EC2 Instance Preparation

## Launch EC2 Instance

- Open AWS EC2 Console
- Launch Ubuntu 22.04 LTS Instance
- Select `t2.micro`
- Create Key Pair


## Configure Security Group

| Type | Port |
|---|---|
| SSH | 22 |
| HTTP | 80 |
| Flask App | 5000 |
| Jenkins | 8080 |
| SonarQube | 9000 |


## Connect to EC2

```bash
ssh -i key.pem ubuntu@<ec2-public-ip>
```

---

# Step 2: Install Dependencies on EC2

## Update Packages

```bash
sudo apt update && sudo apt upgrade -y
```

## Install Docker, Git, Compose

```bash
sudo apt install git docker.io docker-compose-v2 -y
```

## Enable Docker

```bash
sudo systemctl start docker
sudo systemctl enable docker
```

## Add User to Docker Group

```bash
sudo usermod -aG docker $USER
newgrp docker
```

---

# Step 3: Jenkins Installation and Setup

## Install Java

```bash
sudo apt install openjdk-21-jdk -y
```

## Install Jenkins

```bash
curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key | sudo tee /usr/share/keyrings/jenkins-keyring.asc > /dev/null
```

```bash
echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] https://pkg.jenkins.io/debian-stable binary/ | sudo tee /etc/apt/sources.list.d/jenkins.list > /dev/null
```

```bash
sudo apt update
sudo apt install jenkins -y
```

## Start Jenkins

```bash
sudo systemctl start jenkins
sudo systemctl enable jenkins
```

## Get Jenkins Password

```bash
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
```

Open:

```text
http://<ec2-public-ip>:8080
```

## Give Docker Permission to Jenkins

```bash
sudo usermod -aG docker jenkins
sudo systemctl restart jenkins
```
# Install SonarQube
```bash
docker run -d --name sonarqube -p 9000:9000 sonarqube:lts-community
```
---

Verify the installation:

- python --version
- git --version
- docker --version
- docker compose version
- java -version
- jenkins --version
  
# Step 4: Clone Repository

```bash
git clone https://github.com/rajakumarck28/Automated-CICD-Pipeline-for-Containerized-Flask-Application.git
```
```bash
cd Automated-CICD-Pipeline-for-Containerized-Flask-Application
```

---

# Dockerfile

```dockerfile
FROM python:3.9

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir flask flask-mysqldb bcrypt mysqlclient

EXPOSE 5000

CMD ["python", "app.py"]
```
# Run the Application Locally

## Docker

Build Docker Image
```bash
docker build -t akshay9480/flask-auth-app:latest .
```
Run Docker Container
```bash
docker run -d \
-p 5000:5000 \
--name flask-auth-app \
akshay9480/flask-auth-app:latest
```
Check Running Containers
```bash
docker ps
```

# docker-compose.yml

```yaml
version: '3.8'

services:

  flask-app:
    image: akshay9480/flask-auth-app:latest
    container_name: flask-auth-app

    ports:
      - "5000:5000"

    depends_on:
      - mysql-db

    environment:
      MYSQL_HOST: mysql-db
      MYSQL_USER: root
      MYSQL_PASSWORD: root123
      MYSQL_DB: authapp

    restart: always

  mysql-db:
    image: mysql:8

    container_name: mysql-db

    environment:
      MYSQL_ROOT_PASSWORD: root123
      MYSQL_DATABASE: authapp

    ports:
      - "3306:3306"

    restart: always

    volumes:
      - mysql-data:/var/lib/mysql

volumes:
  mysql-data:
```
## Docker Compose
Docker Compose makes it easy to build and run the application with a single command.

Build and Start
```bash
docker compose up --build -d
```

# Jenkinsfile

```groovy
pipeline {
    agent any

    environment {
        IMAGE_NAME = "akshay9480/flask-auth-app"
        IMAGE_TAG = "latest"
        DOCKER_CREDS = "Dockerhub"
    }

    stages {

        stage('Clone Code') {
            steps {
                git branch: 'main',
                url: 'https://github.com/rajakumarck28/Automated-CICD-Pipeline-for-Containerized-Flask-Application.git'
            }
        }

        stage('SonarQube Scan') {
            steps {
                script {
                    def scannerHome = tool 'SonarScanner'

                    withSonarQubeEnv('SonarQube') {
                        sh """
                        ${scannerHome}/bin/sonar-scanner \
                        -Dsonar.projectKey=flask-auth-app \
                        -Dsonar.projectName=flask-auth-app \
                        -Dsonar.sources=. \
                        -Dsonar.python.version=3
                        """
                    }
                }
            }
        }

        stage('Quality Gate') {
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: false
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                sh "docker build -t ${IMAGE_NAME}:${IMAGE_TAG} ."
            }
        }

        stage('Push Docker Image') {
            steps {
                script {
                    docker.withRegistry('', DOCKER_CREDS) {
                        def image = docker.image("${IMAGE_NAME}:${IMAGE_TAG}")
                        image.push()
                    }
                }
            }
        }

        stage('Docker Compose Rebuild') {
            steps {
                sh '''
                docker-compose up -d --build
                '''
            }
        }
    }

    post {
        success {
            echo 'Application deployed successfully!'
        }

        failure {
            echo 'Pipeline Failed!'
        }
    }
}
```
# CI/CD Pipeline Overview
The Jenkins pipeline automates the following tasks:
- Checkout source code from GitHub.
- Build the Flask application.
- Run SonarQube static code analysis.
- Validate the SonarQube Quality Gate.
- Build the Docker image.
- Push the Docker image to Docker Hub.
- Deploy the application (optional).

# Pipeline Flow
```text
GitHub
   │
   ▼
Jenkins
   │
   ├── Checkout
   ├── SonarQube Analysis
   ├── Quality Gate
   ├── Docker Build
   ├── Docker Push
   └── Deploy
```

# SonarQube Integration
SonarQube is integrated into the Jenkins pipeline to perform static code analysis and enforce code quality before building the Docker image.
SonarQube Analysis Includes
- Bugs Detection
- Vulnerability Analysis
- Code Smells
- Duplicated Code Detection
- Maintainability Rating
- Reliability Rating
- Security Rating
- Quality Gate Validation

SonarScanner Command
```bash
sonar-scanner \
-Dsonar.projectKey=flask-auth-app \
-Dsonar.sources=. \
-Dsonar.host.url=http://<SONARQUBE_SERVER>:9000 \
-Dsonar.token=<SONAR_TOKEN>
```
# Jenkins Credentials
Configure the following credentials in Jenkins before running the pipeline.

```text
┌──────────────────────────────────┬──────────────────────────────────────────┐
│ Credential                       │ Purpose                                  │
├──────────────────────────────────┼──────────────────────────────────────────┤
│ GitHub Credentials               │ Clone repository                         │
├──────────────────────────────────┼──────────────────────────────────────────┤
│ SonarQube Token                  │ Static Code Analysis                     │
├──────────────────────────────────┼──────────────────────────────────────────┤
│ Docker Hub Username              │ Image Push                               │
├──────────────────────────────────┼──────────────────────────────────────────┤
│ Docker Hub Personal Access Token │ Docker Authentication                    │
└──────────────────────────────────┴──────────────────────────────────────────┘

```
# Jenkins Pipeline Creation and Execution
## Create Jenkins Pipeline

- New Item
- Pipeline
- Pipeline Script from SCM
- Git
- Add GitHub Repository URL

## Build Pipeline

Click:

```text
Build Now
```

## Verify Containers

```bash
docker ps
```

## Access Application

```text
http://<ec2-public-ip>:5000
```
# Jenkins Pipeline Stages
The Jenkins pipeline automates the entire software delivery process.

1️⃣ Checkout Source Code
- Pulls the latest source code from GitHub.

2️⃣ Install Dependencies
- Installs all Python packages required by the Flask application.
pip install -r requirements.txt

3️⃣ SonarQube Code Analysis
- Executes SonarScanner.
- Uploads the analysis report to SonarQube.

4️⃣ Quality Gate
- Jenkins waits for SonarQube to complete the analysis.
- If the Quality Gate fails, the pipeline stops.
- If it passes, the pipeline proceeds to build the Docker image.

5️⃣ Build Docker Image
- docker build -t akshay9480/flask-auth-app:latest .

6️⃣ Push Docker Image
- docker push akshay9480/flask-auth-app:latest

7️⃣ Deployment
- The Docker image can be deployed through Docker compose

# After a successful pipeline execution:
- Docker image is tagged automatically.
- Image is pushed to Docker Hub.
- Latest version is available for deployment.

Example:
docker pull akshay9480/flask-auth-app:latest

Docker Hub Repository:
https://hub.docker.com/r/akshay9480/flask-auth-app

# Complete CI/CD Workflow
```text
Developer
    │
    ▼
Git Push
    │
    ▼
GitHub Repository
    │
    ▼
Jenkins Pipeline
    │
    ├── Checkout Source
    ├── Install Dependencies
    ├── SonarQube Scan
    ├── Quality Gate Validation
    ├── Build Docker Image
    ├── Push Docker Image
    └── Deploy Application (Optional)
```



# Troubleshooting
## SonarQube Quality Gate Failed
- Verify SonarQube server is running.
- Check project Quality Gate conditions.
- Review the analysis report in SonarQube.

## Docker Login Failed
- docker login
- Ensure you use your Docker Hub Personal Access Token instead of your account password.

## Docker Push Failed
Verify:
- Docker login is successful.
- Repository name is correct.
- Docker image is tagged correctly.
- docker images
- docker push akshay9480/flask-auth-app:latest

## Jenkins Pipeline Failed
Check:
- Jenkins Console Output
- SonarQube Logs
- Docker Logs
- Jenkins Credentials
- GitHub Webhook Configuration
---

# Conclusion

This project demonstrates an end-to-end CI/CD pipeline for a containerized Flask application using GitHub, Jenkins, SonarQube, Docker, Docker Hub, Docker Compose, and MySQL. It automates code integration, quality analysis, Docker image creation, image publishing, and application deployment. The project highlights practical DevOps skills in CI/CD automation, containerization, code quality, and deployment, providing a scalable and reliable software delivery workflow.

---
# Future Enhancements
- Kubernetes Deployment
- AWS EKS Integration
- NGINX Reverse Proxy
- HTTPS with SSL/TLS
- GitHub Webhook Integration
- Automated Unit & Integration Testing
- Monitoring with Prometheus & Grafana

# Jenkins Pipeline
<img width="1920" height="1080" alt="Screenshot (55)" src="https://github.com/user-attachments/assets/2ec07bcf-8129-46c1-bd3a-11cc9be4571d" />

# Security Groups 
<img width="1920" height="1080" alt="Screenshot (57)" src="https://github.com/user-attachments/assets/42cc6cce-7184-49d2-9002-fcade77a7782" />

# Running containers 
<img width="1920" height="1080" alt="Screenshot (56)" src="https://github.com/user-attachments/assets/060cddce-b2b1-4199-a7f3-6af51ee15aa8" />

# Web application loginpage
<img width="1920" height="1080" alt="Screenshot (54)" src="https://github.com/user-attachments/assets/ee21fdde-5bb3-43c9-abf8-a16c76054bcb" />
<img width="1920" height="1080" alt="Screenshot (53)" src="https://github.com/user-attachments/assets/6bf31ae1-6dd8-426f-bbfc-93cae0664306" />






