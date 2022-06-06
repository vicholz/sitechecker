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

command="python3 sitechecker.py --data ma1.json"

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
def subject = "MA1 BB is in stock!"
def details = """
<a href='https://www.bestbuy.com/site/motorola-wireless-car-adapter-for-android-auto-black/6505050.p?skuId=6505050'>LINK</a><br>
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
