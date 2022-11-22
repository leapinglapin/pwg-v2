#!/usr/bin/env groovy

node {
    checkout scm
    def djangoImage
    def nodeImage
    stage('Build') {
        echo 'Building...'
        nodeImage = docker.image('node:12.22.7')
        nodeImage.inside('-v /output/:/output/ -u root'){
            sh 'rm -r ./tailwind/static/* ./shopcgt/static/js/cgt/* ./static/* || true'
            sh 'rm -r /output/css/* /output/js/* || true'
            sh 'yarn install'
            sh 'yarn build'
            sh 'cp -r ./tailwind/static/css/ /output/css/'
            sh 'cp -r ./shopcgt/static/js/cgt/ /output/js/'
        }
        djangoImage = docker.build("registry.digitalocean.com/cgt/shopcgt:${env.BUILD_ID}")
        djangoImage.inside('-v /output/:/output/ -u root'){
            sh 'mkdir -p shopcgt/static/js/cgt/'
            sh 'cp -r /output/css/ shopcgt/static/css/'
            sh 'cp -r /output/js/ shopcgt/static/js/cgt/'
        }
    }
    stage('Test') {
        echo 'Testing...'
        //test npm here
        withCredentials([file(credentialsId: 'prod.env', variable: 'env_file')]){
            djangoImage.inside('-u root --env-file $env_file'){
                sh 'cd /app/'
                sh './manage.py test --no-input --keepdb'
            }
        }
    }
    stage('Deploy'){
        echo 'Deploying...'
        djangoImage.inside('-u root'){
            sh 'cd /app/'
            sh './manage.py collectstatic --no-input'
        }
        docker.withRegistry('https://registry.digitalocean.com/cgt/', 'dodockerauth'){
            djangoImage.push()
            djangoImage.push('latest')
        }
        // Run migrations on the database
        withCredentials([file(credentialsId: 'prod.env', variable: 'env_file')]){
            djangoImage.inside('-u root --env-file $env_file'){
                sh 'cd /app/'
                sh './manage.py migrate'
            }
        }
        sh 'doctl apps create-deployment doappcluserid'
    }
}
