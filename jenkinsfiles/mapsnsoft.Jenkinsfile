pipeline {
    agent any
    options {
        buildDiscarder(logRotator(numToKeepStr: '10', artifactNumToKeepStr: '10'))
        ansiColor('xterm')
        timestamps()
    }
    triggers {
        cron('0 10 * * *')
    }
    stages {
        stage ('Site Checker - Run') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'MAPSNSOFT',
                        usernameVariable: 'MAPSNSOFT_USER',
                        passwordVariable: 'MAPSNSOFT_PASS'
                    )])
                {
                    sh '''
set +x

python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt

export DISPLAY=:0

rm -rf **/*.log **/*.png

if [ -n "${DATA}" ]; then
    DATA_PARAM="--data ${DATA}"
fi

if [ "${VERBOSE}" == "true" ]; then
    VERBOSE_PARAM="--verbose"
fi

command="python3 sitechecker.py --data configs/mapsnsoft.json"

echo "Executing '${command}'..."
eval $command
                    '''
                }
            }
        }
    }
    post {
        always {
            archiveArtifacts artifacts: '**/*.png,**/*.log', fingerprint: true
            script {
def SUBJECT = "Kia Mapnsoft Update Available!"
def CONTENT = """
<a href='https://mapnsoft.com/kia/customer/account/login/#dashboard'>SITE URL</a><br>
<a href='${env.BUILD_URL}/console'>CONSOLE</a><br>
<a href='${env.BUILD_URL}/artifact'>ARTIFACTS</a>
"""

if ("${currentBuild.currentResult}" != "SUCCESS" || currentBuild.getPreviousBuild().result != currentBuild.currentResult){
    // emailext (
    //     subject: EMAIL_SUBJECT,
    //     body: EMAIL_CONTENT,
    //     to: "${env.EMAIL_DEFAULT}",
    //     attachmentsPattern: '**/*.png,**/*.log'
    // )
    withCredentials([string(credentialsId: 'GOOGLE_CHAT_TOKEN', variable: 'GOOGLE_CHAT_TOKEN')]) {
        hangoutsNotify(
            token: "$GOOGLE_CHAT_TOKEN",
            threadByJob: true,
            sameThreadNotification: true,
            messageFormat: "simple",
            message: "${CONTENT}",
        )
    }
}
            }
        }
    }
}
