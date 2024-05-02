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
    emailext (
        subject: EMAIL_SUBJECT,
        body: EMAIL_CONTENT,
        to: "${env.EMAIL_DEFAULT}",
        attachmentsPattern: '**/*.png,**/*.log'
    )
}

            }
        }
    }
}
