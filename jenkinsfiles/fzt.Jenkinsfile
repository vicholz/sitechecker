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

python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt

command="python3 sitechecker.py --data configs/fzt.json"

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
def subject = "FZT is in stock!"
def details = """
<a href='${env.BUILD_URL}/console'>CONSOLE</a><br>
<a href='${env.BUILD_URL}/artifact'>ARTIFACTS</a>
"""

// if ("${currentBuild.currentResult}" != "SUCCESS" && currentBuild.getPreviousBuild().result != currentBuild.currentResult){
//     emailext (
//         subject: subject,
//         body: details,
//         to: "${env.EMAIL_DEFAULT}",
//         attachmentsPattern: '**/*.png,**/*.log'
//     )
// }
            }
        }
    }
}
