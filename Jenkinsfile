pipeline {
    agent any
    options {
        buildDiscarder(logRotator(numToKeepStr: '10', artifactNumToKeepStr: '10'))
        ansiColor('xterm')
        timestamps()
    }
    triggers {
        cron('* H/4 * * *')
    }
    parameters {
        string(name: 'DATA', defaultValue: 'milk.json', description: 'Task data file (JSON)')
        booleanParam(name: 'VERBOSE', defaultValue: false, description: 'Enable verbose logger output.')
    }
    stages {
        stage ('Site Checker - Checkout') {
            steps {
                checkout([$class: 'GitSCM', branches: [[name: '**']], doGenerateSubmoduleConfigurations: false, extensions: [], submoduleCfg: [], userRemoteConfigs: [[credentialsId: '', url: 'https://github.com/vicholz/sitechecker']]])
            }
        }
        stage ('Site Checker - Run') {
            steps {
                sh '''
set +x

if [ -n "${DATA}" ]; then
    DATA_PARAM="--url ${DATA}"
fi

if [ "${VERBOSE}" == "true" ]; then
    VERBOSE_PARAM="--verbose"
fi

command="python3 sitechecker.py \
--data ${DATA_PARAM}\
${VERBOSE_PARAM}"

echo "Executing '${command}'..."
eval $command
                '''
            }
        }
    }
}

