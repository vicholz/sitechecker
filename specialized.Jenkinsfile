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

command="python3 sitechecker.py --data specialized.json"

echo "Executing '${command}'..."
eval $command
                '''
            }
        }
    }
    post {
        always {
            archiveArtifacts artifacts: '*.png,**/*.log', fingerprint: true
            script {
def subject = "Stumpjumper EVO Elite Alloy is back in stock!"
def details = """
<a hred='https://www.specialized.com/us/en/stumpjumper-evo-elite-alloy/p/199211?color=318420-199211&searchText=96322-4004'>LINK</a><br>
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
