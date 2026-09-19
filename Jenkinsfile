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
} this my jenkinsfile i want deploy through eks
