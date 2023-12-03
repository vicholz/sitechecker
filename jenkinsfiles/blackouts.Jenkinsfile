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
            archiveArtifacts artifacts: '*.png,**/*.log,**/*.txt', fingerprint: true
            script {
def subject = "BLACKOUTS ARE COMING!"
def details = """
<a href='https://www.pge.com/en_US/residential/outages/planning-and-preparedness/safety-and-preparedness/find-your-rotating-outage-block/find-your-rotating-outage-block.page?WT.mc_id=Vanity_rotatingoutages'>LINK</a><br>
<a href='${env.BUILD_URL}/console'>CONSOLE</a><br>
<a href='${env.BUILD_URL}/artifact'>ARTIFACTS</a>
"""

if ("${currentBuild.currentResult}" != "SUCCESS" && currentBuild.getPreviousBuild().result != currentBuild.currentResult){
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
