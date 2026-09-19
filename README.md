# CI/CD Pipeline for Containerized Application Deployment on AWS EKS

##  Project Overview

This project demonstrates an end-to-end **CI/CD pipeline for deploying a containerized Flask application to Amazon EKS using AWS Fargate**.

The pipeline automates the complete application delivery process, starting from source code checkout and code-quality analysis to Docker image creation, Amazon ECR image storage, and deployment to an Amazon EKS Fargate environment.

The project uses **Jenkins** as the CI/CD automation server, **SonarQube** for static code analysis, **Docker** for containerization, **Amazon ECR** as the container registry, and **Amazon EKS with AWS Fargate** for Kubernetes-based application deployment.

---

##  Architecture

```text
                         Developer
                             |
                             v
                         GitHub
                             |
                             v
                         Jenkins
                             |
             +---------------+---------------+
             |                               |
             v                               v
       Clone Source                    SonarQube
                                             |
                                             v
                                       Quality Gate
                                             |
                                             v
                                      Docker Build
                                             |
                                             v
                                       Amazon ECR
                                             |
                                             v
                                       Amazon EKS
                                             |
                                             v
                                      Kubernetes Service
                                             |
                                             v
                                      AWS Load Balancer
                                             |
                                             v
                                           Users
```

---

## 🛠️ Technologies Used

| Technology        | Purpose                                |
| ----------------- | -------------------------------------- |
| GitHub            | Source code management                 |
| Jenkins           | CI/CD automation                       |
| SonarQube         | Static code analysis                   |
| Docker            | Application containerization           |
| Amazon ECR        | Docker image registry                  |
| Amazon EKS        | Managed Kubernetes                     |
| Kubernetes        | Container orchestration                |
| AWS IAM           | Authentication and authorization       |
| AWS Load Balancer | Application access from the internet   |
| Python / Flask    | Application framework                  |

---

## 🔄 CI/CD Pipeline Flow

The Jenkins pipeline performs the following steps:

```text
1. Clone Code
       ↓
2. SonarQube Scan
       ↓
3. Quality Gate
       ↓
4. Build Docker Image
       ↓
5. Login to Amazon ECR
       ↓
6. Push Docker Image to ECR
       ↓
7. Configure kubectl for EKS
       ↓
8. Deploy Kubernetes Resources
       ↓
9. Update Application Image
       ↓
10. Verify Deployment
```

---

## 🚀 Implemented

### 1. GitHub Integration

* Source code is maintained in GitHub.
* Jenkins automatically checks out the `main` branch.
* The pipeline starts the application delivery process from the GitHub repository.

### 2. SonarQube Static Code Analysis

* Integrated SonarQube with Jenkins.
* Performs static code analysis on the Flask application.
* Uses a dedicated SonarQube project.
* Quality Gate is checked before continuing with the deployment.

### 3. Docker Containerization

* Created a Dockerfile for the Flask application.
* Jenkins automatically builds the Docker image.
* Each Jenkins build generates a unique image tag using the Jenkins build number.

Example:

```text
flask-auth-app:15
flask-auth-app:16
flask-auth-app:17
```

### 4. Amazon ECR

* Docker images are pushed to Amazon Elastic Container Registry.
* Jenkins authenticates to ECR using the AWS CLI.
* The Jenkins EC2 server uses an attached IAM role instead of storing AWS access keys in the Jenkinsfile.

Example image:

```text
123456789012.dkr.ecr.ap-south-1.amazonaws.com/flask-auth-app:15
```

### 5. Amazon EKS

* Created an Amazon EKS cluster for Kubernetes deployment.
* Kubernetes Deployment manages the Flask application Pods.
* Kubernetes Service exposes the application.

### 6. Kubernetes Deployment

The application runs with multiple replicas:

```yaml
replicas: 2
```

This provides two Flask Pods for the application.

### 7. Kubernetes Service

The application is exposed using:

```yaml
type: LoadBalancer
```

AWS provisions a load balancer to provide external access to the Flask application.

---

# 📁 Project Structure

```text
CI-CD-Pipeline-for-Containerized-Application-Deployment-on-Amazon-EKS/
│
├── Dockerfile
├── Jenkinsfile
├── requirements.txt
├── app.py
│
└── k8s/
    ├── deployment.yaml
    └── service.yaml
```

---

# ⚙️ Prerequisites

Before running the project, install/configure:

* AWS Account
* Git
* Docker
* Jenkins
* SonarQube
* AWS CLI
* kubectl
* eksctl
* Amazon ECR
* Amazon EKS
* AWS Fargate

The Jenkins server should have access to AWS through an IAM role.

---

#  AWS IAM Configuration

The Jenkins EC2 server uses an **IAM role** to access AWS services.

No AWS access key or secret key is hardcoded in the Jenkinsfile.

Verify the IAM role:

```bash
aws sts get-caller-identity
```

The Jenkins IAM role requires permissions for the required ECR and EKS operations.

For a learning environment, `AdministratorAccess` can be used, although a production implementation should use a least-privilege IAM policy.

---

#  Create ECR Repository

Create the ECR repository:

```bash
aws ecr create-repository \
  --repository-name flask-auth-app \
  --region ap-south-1
```

Verify:

```bash
aws ecr describe-repositories \
  --repository-name flask-auth-app \
  --region ap-south-1
```

---

#  Create EKS Fargate Cluster

Create an EKS cluster:

```bash
eksctl create cluster \
  --name flask-eks-cluster \
  --region ap-south-1 \
  --fargate
```

Create the application namespace:

```bash
kubectl create namespace flask-app
```

Create a Fargate profile:

```bash
eksctl create fargateprofile \
  --cluster flask-eks-cluster \
  --region ap-south-1 \
  --name flask-profile \
  --namespace flask-app
```

Verify:

```bash
eksctl get fargateprofile \
  --cluster flask-eks-cluster \
  --region ap-south-1
```

---

#  Docker Image

Build the image locally:

```bash
docker build -t flask-auth-app .
```

Run locally:

```bash
docker run -p 5000:5000 flask-auth-app
```

The application should then be accessible on:

```text
http://localhost:5000
```

---

#  Kubernetes Deployment

Example `deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment

metadata:
  name: flask-app
  namespace: flask-app

spec:
  replicas: 2

  selector:
    matchLabels:
      app: flask-app

  template:
    metadata:
      labels:
        app: flask-app

    spec:
      containers:
        - name: flask-app

          image: YOUR_AWS_ACCOUNT_ID.dkr.ecr.ap-south-1.amazonaws.com/flask-auth-app:latest

          imagePullPolicy: Always

          ports:
            - containerPort: 5000
```

---

#  Kubernetes Service

Example `service.yaml`:

```yaml
apiVersion: v1
kind: Service

metadata:
  name: flask-service
  namespace: flask-app

spec:
  type: LoadBalancer

  selector:
    app: flask-app

  ports:
    - protocol: TCP
      port: 80
      targetPort: 5000
```

---

#  Jenkins Pipeline

The Jenkins pipeline performs:

```text
GitHub
  ↓
SonarQube
  ↓
Quality Gate
  ↓
Docker Build
  ↓
ECR Login
  ↓
ECR Push
  ↓
EKS Configuration
  ↓
Kubernetes Deployment
  ↓
Fargate Pods
```

The Jenkins server uses its EC2 IAM role for AWS authentication.

No AWS credentials are stored directly in the Jenkinsfile.

---

#  Jenkins Pipeline Stages

### Clone Code

```groovy
stage('Clone Code')
```

Clones the Flask application from GitHub.

### SonarQube Scan

```groovy
stage('SonarQube Scan')
```

Performs static code analysis.

### Quality Gate

```groovy
stage('Quality Gate')
```

Checks the SonarQube quality gate.

### Build Docker Image

```groovy
stage('Build Docker Image')
```

Builds the Flask Docker image.

### Login to Amazon ECR

```groovy
stage('Login to Amazon ECR')
```

Uses:

```bash
aws ecr get-login-password
```

to obtain temporary ECR authentication and authenticate Docker.

### Push Image to ECR

```groovy
stage('Push Image to ECR')
```

Pushes the Docker image to Amazon ECR.

### Deploy to EKS Fargate

```groovy
stage('Deploy to EKS Fargate')
```

Configures `kubectl` and deploys the application to the EKS cluster.

### Verify Deployment

```groovy
stage('Verify Deployment')
```

Checks:

* Pods
* Deployment
* Service

---

#  Verify Deployment

Check Pods:

```bash
kubectl get pods -n flask-app
```

Check Deployment:

```bash
kubectl get deployment -n flask-app
```

Check Service:

```bash
kubectl get svc -n flask-app
```

Check Pod details:

```bash
kubectl describe pod <pod-name> -n flask-app
```

Check application logs:

```bash
kubectl logs <pod-name> -n flask-app
```

---

#  Access the Application

Get the Load Balancer hostname:

```bash
kubectl get svc flask-service \
  -n flask-app
```

Or:

```bash
kubectl get svc flask-service \
  -n flask-app \
  -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'
```

Open the returned hostname in a browser:

```text
http://<LOAD-BALANCER-DNS>
```

---

#  Continuous Deployment

Every new GitHub/Jenkins build can create a new Docker image version.

Example:

```text
Build 1 → flask-auth-app:1
Build 2 → flask-auth-app:2
Build 3 → flask-auth-app:3
```

Jenkins then updates the Kubernetes Deployment:

```bash
kubectl set image deployment/flask-app \
flask-app=<ECR_IMAGE>:<BUILD_NUMBER> \
-n flask-app
```

Kubernetes performs a rolling update of the application Pods.

---

#  Security

The project avoids storing AWS access keys directly in the Jenkinsfile.

AWS authentication follows:

```text
Jenkins EC2
     ↓
IAM Role
     ↓
AWS CLI
     ↓
ECR / EKS
```

This is preferable to hardcoding:

```text
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
```

inside source code.

---

#  AWS Cost Consideration

This project uses AWS services that may generate charges, including:

* Amazon EKS
* Amazon ECR
* AWS Load Balancer
* Other associated AWS resources

Delete resources after completing the project if they are no longer required.

Delete the EKS cluster:

```bash
eksctl delete cluster \
  --name flask-eks-cluster \
  --region ap-south-1
```

---

# Project Outcome

This project demonstrates an automated cloud-native CI/CD workflow:

```text
Source Code
     ↓
GitHub
     ↓
Jenkins
     ↓
SonarQube
     ↓
Docker
     ↓
Amazon ECR
     ↓
Amazon EKS
     ↓
AWS Fargate
     ↓
Kubernetes
     ↓
AWS Load Balancer
     ↓
Flask Application
```

The implementation demonstrates practical experience with **CI/CD automation, containerization, Kubernetes deployment, AWS ECR, Amazon EKS, AWS Fargate, IAM-based authentication, and automated application delivery**.


<img width="1920" height="1080" alt="Screenshot (70)" src="https://github.com/user-attachments/assets/a1eb1635-6e61-4355-8194-78f26df2beae" />
<img width="1920" height="1080" alt="Screenshot (71)" src="https://github.com/user-attachments/assets/1a5ba0bd-929d-4fb1-ade6-19f75df4ae68" />
<img width="1920" height="1080" alt="Screenshot (72)" src="https://github.com/user-attachments/assets/0617170c-f110-414b-b342-4402cdbd40c7" />
<img width="1920" height="1080" alt="Screenshot (73)" src="https://github.com/user-attachments/assets/30743d80-1329-46b8-8e02-05c1ddd947cd" />
<img width="1920" height="1080" alt="Screenshot (74)" src="https://github.com/user-attachments/assets/d90051c1-d7a3-4216-8dcb-118fd6bb3133" />
<img width="1920" height="1080" alt="Screenshot (75)" src="https://github.com/user-attachments/assets/45a5b3a3-8daa-4f05-99fc-14422f898870" />

