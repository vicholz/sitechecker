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
    parameters {
        string(name: 'DATA', defaultValue: '', description: 'Task data file (JSON)')
        booleanParam(name: 'VERBOSE', defaultValue: false, description: 'Enable verbose logger output.')
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

command="python3 sitechecker.py \
${DATA_PARAM} \
${VERBOSE_PARAM}"

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
def subject = "${currentBuild.currentResult}: Job ${env.JOB_NAME} - #${env.BUILD_NUMBER}"
def details = """
<a href='${env.BUILD_URL}/console'>CONSOLE</a><br>
<a href='${env.BUILD_URL}/artifact'>ARTIFACTS</a>
"""

if ("${currentBuild.currentResult}" != "SUCCESS"){
    emailext (
        subject: subject,
        body: details,
        to: "${env.EMAIL_DEFAULT}",
        attachmentsPattern: '**/*.png,**/*.log'
    )
}
            }
        }
    }
}

