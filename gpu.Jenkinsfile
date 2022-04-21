pipeline {
    agent any
    options {
        buildDiscarder(logRotator(numToKeepStr: '10', artifactNumToKeepStr: '10'))
        ansiColor('xterm')
        timestamps()
    }
    triggers {
        cron('* H/4 * * *')
    }
    stages {
        stage ('Site Checker - Checkout') {
            steps {
                checkout([$class: 'GitSCM', branches: [[name: '**']], doGenerateSubmoduleConfigurations: false, extensions: [], submoduleCfg: [], userRemoteConfigs: [[credentialsId: '', url: 'https://github.com/vicholz/sitechecker']]])
            }
        }
        stage ('Site Checker - Run') {
            steps {
                sh '''
set +x

if [ -n "${DATA}" ]; then
    DATA_PARAM="--data ${DATA}"
fi

if [ "${VERBOSE}" == "true" ]; then
    VERBOSE_PARAM="--verbose"
fi

command="python3 sitechecker.py --data gpu.json"

echo "Executing '${command}'..."
eval $command
                '''
            }
        }
    }
    post {
        always {
            archiveArtifacts artifacts: '*.png', fingerprint: true
            script {
def subject = "GPU STOCK CHANGE DETECTED!"
def details = """
<a href='https://www.bestbuy.com/site/nvidia-geforce-rtx-3080-ti-12gb-gddr6x-pci-express-4-0-graphics-card-titanium-and-black/6462956.p?skuId=6462956'>3080TI</a>
"""

if ("${currentBuild.currentResult}" != "SUCCESS"){
    emailext (
        subject: subject,
        body: details,
        to: "${env.EMAIL_GPU}"
    )
}
            }
        }
    }
}
