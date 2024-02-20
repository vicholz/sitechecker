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

rm -rf *.log *.png

command="python3 sitechecker.py --data blackouts.json"
echo "Executing '${command}'..."
eval $command

echo "Checking for block '${PGE_BLOCK}'..."
cat BLACKOUTS.txt
echo
if (grep ${PGE_BLOCK} BLACKOUTS.txt); then
    echo "Found block '${PGE_BLOCK}'"
    exit 1
else
    echo "Did not find block '${PGE_BLOCK}'"
    exit 0
fi
                '''
            }
        }
    }
    post {
        always {
            archiveArtifacts artifacts: '**/*.png,**/*.log', fingerprint: true
            script {
def EMAIL_SUBJECT = "PG&E Blackouts are coming!"
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
