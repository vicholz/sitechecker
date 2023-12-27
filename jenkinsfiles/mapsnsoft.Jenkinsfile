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
                withCredentials([
                    usernamePassword(
                        credentialsId: 'MAPSNSOFT',
                        usernameVariable: 'MAPSNSOFT_USER',
                        passwordVariable: 'MAPSNSOFT_PASS'
                    )])
                {
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
                def subject = "Maps have been updated!"
                def details = """
                <a hred='https://www.mapnsoft.com/kia/mapnsoft/product/search/c/USA/y/206/m/182'>LINK</a><br>
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
                sh '''
                    curl \
                        -X POST \
                        --data-urlencode "payload={ \
                        \"text\": \"$JOB_NAME status has changed. See $GIT_URL for config details.\" \
                        }" \
                        $SLACK_WEBHOOK_URL
                '''
            }
        }
    }
}
