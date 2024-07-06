pipeline {
    agent any
    options {
        buildDiscarder(logRotator(numToKeepStr: '10', artifactNumToKeepStr: '10'))
        ansiColor('xterm')
        timestamps()
    }
    triggers {
        cron('H */4 * * *')
    }
    stages {
        stage ('Site Checker - Run') {
            steps {
                sh '''
set +x

python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt

rm -rf **/*.log **/*.png

command="python3 sitechecker.py --data configs/fzt.json"

echo "Executing '${command}'..."
eval $command
                '''
            }
        }
    }
    post {
        always {
            archiveArtifacts artifacts: '**/*.png,**/*.log', fingerprint: true
            script {
def EMAIL_SUBJECT = "FZT is in stock!"
def EMAIL_CONTENT = """
<a href='https://shop.flipperzero.one/products/flipper-zero-transparent'>SITE URL</a><br>
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
