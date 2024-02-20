pipeline {
    agent any
    options {
        buildDiscarder(logRotator(numToKeepStr: '10', artifactNumToKeepStr: '10'))
        ansiColor('xterm')
        timestamps()
    }
    triggers {
        cron('0 H/4 * * *')
    }
    stages {
        stage ('Site Checker - Run') {
            steps {
                sh '''
set +x

export DISPLAY=:0

rm -rf *.log *.png

if [ -n "${DATA}" ]; then
    DATA_PARAM="--data ${DATA}"
fi

if [ "${VERBOSE}" == "true" ]; then
    VERBOSE_PARAM="--verbose"
fi

python3 -m venv .venv
. .venv/bin/activate

pip3 install -U -r requirements.txt

command="python3 sitechecker.py --data configs/dell.json"

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
def EMAIL_SUBJECT = "Dell BIOS Update Available!"
def EMAIL_CONTENT = """
<a href='${env.BUILD_URL}/console'>CONSOLE</a><br>
<a href='${env.BUILD_URL}/artifact'>ARTIFACTS</a>
"""
                if ("${currentBuild.currentResult}" != "SUCCESS" && currentBuild.getPreviousBuild().result != currentBuild.currentResult){
                    sh """
curl --request POST \
--url https://api.sendgrid.com/v3/mail/send \
--header 'Authorization: Bearer ${SENDGRID_API_KEY}' \
--header 'Content-Type: application/json' \
--data '{"personalizations":[{"to":[{"email":"${DEFAULT_EMAIL}"}],"subject":"${EMAIL_SUBJECT}"}],"content":[{"type":"text/plain","value":"${EMAIL_CONTENT}"}],"from":{"email":"${DEFAULT_EMAIL}","name":"Jenkins@TinyHoot"},"reply_to":{"email":"${DEFAULT_EMAIL}","name":"Jenkins@TinyHoot"}}'
                    """
                }
            }
        }
    }
}
