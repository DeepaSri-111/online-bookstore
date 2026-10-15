
pipeline {
    agent any

    parameters {
        choice(
            name: 'RELEASE_MODE',
            choices: ['NORMAL', 'FAULTY_TEST'],
            description: 'NORMAL deploys the build image; FAULTY_TEST tests automatic rollback.'
        )
    }
    options {
        skipDefaultCheckout(true)
        timestamps()
    }

    environment {
        IMAGE_NAME = 'deepasri111/online-bookstore'
        DEPLOYMENT_NAME = 'online-bookstore-deployment'
        CONTAINER_NAME = 'online-bookstore'
        SERVICE_NAME = 'online-bookstore-service'
    }

    stages {
        stage('Checkout Source Code') {
            steps {
                checkout scm
                bat 'git status --short'
            }
        }

        stage('Automated Tests') {
            steps {
                bat '"C:\\Users\\tdees\\AppData\\Local\\Programs\\Python\\Python312\\python.exe" test.py'
            }
        }

        stage('Security Gate') {
            steps {
                script {
                    def scanResult = bat(
                        returnStatus: true,
                        script: '''
                        findstr /S /I /N /C:"password=" /C:"secret=" /C:"api_key=" *.html *.js *.py *.yaml Dockerfile
                        '''
                    )

                    if (scanResult == 0) {
                        error('Security gate failed: review possible hard-coded secrets in source files.')
                    }
                }
                echo 'Security gate passed: no checked secret patterns found.'
            }
        }

        stage('Build Docker Image') {
            steps {
                bat 'docker build -t %IMAGE_NAME%:%BUILD_NUMBER% .'
            }
        }

        stage('Push Docker Image') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-credentials',
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_TOKEN'
                    )
                ]) {
                    bat 'echo %DOCKER_TOKEN%| docker login -u "%DOCKER_USER%" --password-stdin'
                    bat 'docker push %IMAGE_NAME%:%BUILD_NUMBER%'
                }
            }
        }

        stage('Verify Kubernetes Access') {
            steps {
                withCredentials([
                    file(
                        credentialsId: 'kubeconfig-file',
                        variable: 'KUBECONFIG'
                    )
                ]) {
                    bat 'kubectl get nodes'
                    bat 'kubectl get deployment %DEPLOYMENT_NAME%'
                    bat 'kubectl get service %SERVICE_NAME%'
                }
            }
        }

         

stage('Deploy to Kubernetes') {
    steps {
        withCredentials([
            file(
                credentialsId: 'kubeconfig-file',
                variable: 'KUBECONFIG'
            )
        ]) {
            script {
                def targetImage

                if (params.RELEASE_MODE == 'FAULTY_TEST') {
                    targetImage = "${env.IMAGE_NAME}:bad-version"
                    echo 'FAULTY TEST: deploying an intentionally invalid image.'
                } else {
                    targetImage = "${env.IMAGE_NAME}:${env.BUILD_NUMBER}"
                    echo "Normal deployment: ${targetImage}"
                }

                bat "kubectl set image deployment/${env.DEPLOYMENT_NAME} ${env.CONTAINER_NAME}=${targetImage}"

                def rolloutResult = bat(
                    returnStatus: true,
                    script: "kubectl rollout status deployment/${env.DEPLOYMENT_NAME} --timeout=60s"
                )

                if (rolloutResult != 0) {
                    echo 'Rollout failed. Starting automatic rollback.'

                    bat "kubectl rollout undo deployment/${env.DEPLOYMENT_NAME}"

                    bat "kubectl rollout status deployment/${env.DEPLOYMENT_NAME} --timeout=120s"

                    error('The new release failed. Automatic rollback was performed.')
                }

                echo 'Deployment rollout succeeded.'
            }
        }
    }
}

        stage('Verify Deployment') {
            steps {
                withCredentials([
                    file(
                        credentialsId: 'kubeconfig-file',
                        variable: 'KUBECONFIG'
                    )
                ]) {
                    bat 'kubectl get deployment %DEPLOYMENT_NAME%'
                    bat 'kubectl get pods -l app=online-bookstore'
                    bat 'kubectl get service %SERVICE_NAME%'
                }
            }
        }
    }

    post {
        success {
            echo 'SUCCESS: Tests and configured gates passed; the bookstore deployment completed.'
        }
        failure {
            echo 'FAILED: A pipeline stage failed. Check its console output before proceeding.'
        }
        always {
            echo 'Online Bookstore CI/CD pipeline finished.'
        }
    }
}
