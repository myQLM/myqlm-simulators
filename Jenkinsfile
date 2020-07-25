#!/usr/local/bin/groovy

// ---------------------------------------------------------------------------
//
// GROOVY GLOBALS
//
// ---------------------------------------------------------------------------
def QLM_VERSION = "1.1.0"

// JOB_NAME:  qat-bdd.el8 | qat-bdd.el8/master
// BRANCH_NAME:   master  | rc
// OS:                el7 | el8
// OSVERSION:         7.8 | 8.2
// OSLABEL:       rhel7.8 | rhel8.2
// JOB_TYPE:      mono    | multi
def OS
def OSVERSION
def OSLABEL
def JOB_TYPE
def DOCKER_IMAGE

OS = "${JOB_NAME}".tokenize('.')[1].tokenize('/')[0]
if ("$OS".contains("el7")) {
    OSVERSION = "7.8"
    LABEL = "master"
} else if ("$OS".contains("el8")) {
    OSVERSION = "8.2"
    LABEL = "master"
}
OSLABEL  = "rhel$OSVERSION"
JOB_TYPE = "multibranch"

if (!env.BRANCH_NAME) {
    BRANCH_NAME = "master"
    JOB_TYPE    = "monobranch"
}
if ("$BRANCH_NAME".contains("rc")) {
    DOCKER_IMAGE = "qlm-reference-${QLM_VERSION}-${OSLABEL}:latest"
} else {
    DOCKER_IMAGE = "qlm-devel-${QLM_VERSION}-${OSLABEL}:latest"
}
HOST_NAME = InetAddress.getLocalHost().getHostName()

// Expose some variables to bash and groovy functions
env.OS = "$OS"
env.BRANCH_NAME="$BRANCH_NAME"
env.HOST_NAME="$HOST_NAME"

// Show the parameters
echo "\
JOB_NAME     = ${JOB_NAME}\n\
BRANCH_NAME  = ${BRANCH_NAME}\n\
JOB_BASE_NAME= ${JOB_BASE_NAME}\n\
JOB_TYPE     = ${JOB_TYPE}\n\
OS           = ${OS}\n\
OSVERSION    = ${OSVERSION}\n\
OSLABEL      = ${OSLABEL}\n\
HOST_NAME    = ${HOST_NAME}\n\
DOCKER_IMAGE = ${DOCKER_IMAGE}\n\
"


// ---------------------------------------------------------------------------
//
// Configure some of the job properties
//
// ---------------------------------------------------------------------------
properties([
    [$class: 'JiraProjectProperty'], 
    buildDiscarder(logRotator(artifactDaysToKeepStr: '', artifactNumToKeepStr: '', daysToKeepStr: '', numToKeepStr: '25')), 
    disableConcurrentBuilds(), 
    pipelineTriggers([pollSCM('')]),
    parameters([
        buildSelector(defaultSelector: lastSuccessful(stable: true), description: '', name: 'UI_RESTORE_ARTIFACT'),
        [$class: 'ChoiceParameter', choiceType: 'PT_CHECKBOX', description: '', filterLength: 1, filterable: false, name: 'UI_SKIP_TESTS', randomName: 'choice-parameter-1783699282894047',
            script: [
                $class: 'GroovyScript',
                fallbackScript: [
                    classpath: [],
                    sandbox: false,
                    script: ' '
                ],
                script: [
                    classpath: [],
                    sandbox: false,
                    script: '''
                        def user = hudson.model.User.current()
                        if ("$user" == "Jenkins")
                           return [\':selected\']
                        else
                           return [\':disabled\']
                    '''
                ]
            ]
        ]
    ])
])


// ---------------------------------------------------------------------------
//
// Declarative pipeline
//
// ---------------------------------------------------------------------------
pipeline
{
    agent {
        docker {
            label "${LABEL}"
            image "${DOCKER_IMAGE}"
            args '-v /data/jenkins/.ssh:/data/jenkins/.ssh -v /opt/qlmtools:/opt/qlmtools -v /var/www/repos:/var/www/repos'
            alwaysPull false
        }
    }

    options {
        ansiColor('xterm')
    }

    environment {
        RUN_BY_JENKINS=1

        BASEDIR           = "$WORKSPACE"
        QATDIR            = "$BASEDIR/qat"
        QAT_REPO_BASEDIR  = "$BASEDIR"
        INSTALL_DIR       = "$BASEDIR/install"
        RUNTIME_DIR       = "$BASEDIR/runtime"

        BLACK   = '\033[30m' ; B_BLACK   = '\033[40m'
        RED     = '\033[31m' ; B_RED     = '\033[41m'
        GREEN   = '\033[32m' ; B_GREEN   = '\033[42m'
        YELLOW  = '\033[33m' ; B_YELLOW  = '\033[43m'
        BLUE    = '\033[34m' ; B_BLUE    = '\033[44m'
        MAGENTA = '\033[35m' ; B_MAGENTA = '\033[45m'
        CYAN    = '\033[36m' ; B_CYAN    = '\033[46m'
        WHITE   = '\033[97m' ; B_WHITE   = '\033[107m'
        BOLD    = '\033[1m'  ; UNDERLINE = '\033[4m'
        RESET   = '\033[0m'

        BUILD_CAUSE      =  currentBuild.getBuildCauses()[0].shortDescription.toString()
        BUILD_CAUSE_NAME =  currentBuild.getBuildCauses()[0].userName.toString()

        REPO_NAME = sh returnStdout: true, script: '''set +x
            echo -n ${JOB_NAME%%.*}
        '''
    } 


    stages
    {
        stage('Init')
        {
            steps {
                echo "${MAGENTA}${BOLD}[INIT]${RESET}"
                echo "\
BASEDIR           = ${BASEDIR}\n\
QATDIR            = ${QATDIR}\n\
QAT_REPO_BASEDIR  = ${QAT_REPO_BASEDIR}\n\
INSTALL_DIR       = ${INSTALL_DIR}\n\
RUNTIME_DIR       = ${RUNTIME_DIR}\n\
BUILD_CAUSE       = ${BUILD_CAUSE}\n\
BUILD_CAUSE_NAME  = ${BUILD_CAUSE_NAME}\n\
REPO_NAME         = ${REPO_NAME}\n\
"

                sh '''set +x
                    mkdir -p $REPO_NAME
                    mv * $REPO_NAME/ 2>/dev/null  || true
                    mv .* $REPO_NAME/ 2>/dev/null || true

                    ATOS_GIT_BASE_URL=ssh://bitbucketbdsfr.fsc.atos-services.net:7999/brq
                    if [[ $HOST_NAME =~ qlmci2 ]]; then
                        ATOS_GIT_BASE_URL=ssh://qlmjenkins@qlmgit.usrnd.lan:29418/qlm
                    fi

                    # Clone qat repo
                    echo -e "--> Cloning qat, branch=$BRANCH_NAME  [$ATOS_GIT_BASE_URL] ..."
                    cmd="git clone --single-branch --branch $BRANCH_NAME $ATOS_GIT_BASE_URL/qat"
                    echo "> $cmd"
                    eval $cmd

                    # Clone cross-compilation repo
                    #echo -e "--> Cloning cross-compilation, branch=$BRANCH_NAME  [$ATOS_GIT_BASE_URL] ..."
                    #cmd="git clone --single-branch --branch $BRANCH_NAME $ATOS_GIT_BASE_URL/cross-compilation"
                    #echo "> $cmd"
                    #eval $cmd
                '''
            }
        } // Init

        stage('Versioning')
        {
            steps {
                echo "${MAGENTA}${BOLD}[VERSIONING]${RESET}"
                script {
                    MYQLM_VERSION = sh returnStdout: true, script: '''set +x
                        if [[ -r qat/share/versions/myqlm.version ]]; then
                            MYQLM_VERSION="$(cat qat/share/versions/myqlm.version)"
                        else
                            echo -e "\n**** No qat/share/versions/myqlm.version file"
                            exit 1
                        fi
                        echo -n $MYQLM_VERSION
                    '''
                    env.MYQLM_VERSION="$MYQLM_VERSION"
                    echo "(wheel) -> ${MYQLM_VERSION}"
                }
                sh '''set +x
                    sed -i "s/version=.*/version=\\"$MYQLM_VERSION\\",/" $WORKSPACE/$REPO_NAME/setup.py
                '''
                buildName "${MYQLM_VERSION}.${BUILD_NUMBER}"
            }
        } // Versioning


        stage('Install')
        {
            steps {
                echo "${MAGENTA}${BOLD}[INSTALL]${RESET}"
                script {
                    sh '''set +x
                        source /usr/local/bin/qatenv
                        mkdir -p $INSTALL_DIR/lib64/python3.6/site-packages/
                        cmd="cp -r ${REPO_NAME}/qat $INSTALL_DIR/lib64/python3.6/site-packages/"
                        echo -e "\n> $cmd"
                        $cmd

                        # Save the artifact(s)
                        echo -e "\nCreating ${REPO_NAME}-${MYQLM_VERSION}.${BUILD_NUMBER}.tar.gz"
                        cd $INSTALL_DIR && tar cfz $WORKSPACE/${REPO_NAME}-${MYQLM_VERSION}.${BUILD_NUMBER}.tar.gz .
                    '''
                    archiveArtifacts artifacts: "${REPO_NAME}-${MYQLM_VERSION}.${BUILD_NUMBER}.tar.gz", onlyIfSuccessful: true
                }
            }
        } // Install


        stage('Tests-dependencies') 
        {
            when {
                not {
                    allOf {
                        equals expected:"true", actual: UI_SKIP_TESTS;
                        anyOf {
                            equals expected:"Jenkins", actual: BUILD_CAUSE_NAME;
                            equals expected:"null", actual: BUILD_CAUSE_NAME
                        }
                    }
                }
            }

            steps {
                echo "${MAGENTA}${BOLD}[TESTS-DEPENDENCIES]${RESET}"
                script {
                    restore_dependencies_install_dir()
                }
            }
        } // Tests-dependencies


        stage('Tests')
        {
            when {
                not {
                    allOf {
                        equals expected:"true", actual: UI_SKIP_TESTS;
                        anyOf {
                            equals expected:"Jenkins", actual: BUILD_CAUSE_NAME;
                            equals expected:"null", actual: BUILD_CAUSE_NAME
                        }
                    }
                }
            }

            steps {
                echo "${MAGENTA}${BOLD}[TESTS]${RESET}"
                script {
                    catchError(buildResult: 'UNSTABLE', stageResult: 'UNSTABLE') {
                        sh '''set +x
                            source /usr/local/bin/qatenv
                            cd $REPO_NAME/tests
                            cmd="python3 -m pytest -v ."
                            echo -e "\n> $cmd"
                            $cmd
                        '''
                    }
                }
            }
        } // Tests


        stage("WHEEL")
        {
            steps {
                echo "${MAGENTA}${BOLD}[WHEEL]${RESET}"
                script {
                    sh '''set +x
                        source /usr/local/bin/qatenv
                        cd $WORKSPACE/$REPO_NAME

                        echo -e "\n${CYAN}Building myQLM wheels...${RESET}"
                        cmd="$PYTHON setup.py bdist_wheel"
                        echo -e "\n> ${GREEN}$cmd${RESET}"
                        $cmd
 
                        echo -e "\n\n${MAGENTA}WHEEL packaged files list${RESET}"
                        find dist -type f -exec echo -e "$BLUE"{}"${RESET}" \\; -exec unzip -l {} \\;
    
                        echo -e "\n\n${MAGENTA}METADATA file${RESET}"
                        find dist -type f -exec unzip -p {} ${REPO_NAME//-/_}-$MYQLM_VERSION.dist-info/METADATA \\;
                    '''
                    // Save the source tarball and wheel artifacts
                    archiveArtifacts artifacts: "${REPO_NAME}-${MYQLM_VERSION}.${BUILD_NUMBER}.tar.gz", onlyIfSuccessful: true
                    archiveArtifacts artifacts: "${REPO_NAME}/dist/*.whl", onlyIfSuccessful: true
                }
            }
        } // wheel
    } // stages


    post
    {
        always
        {
            echo "${MAGENTA}${BOLD}[POST]${RESET}"
            script {
                sh '''set +x
                    rm -f tarballs_artifacts/.*.artifact 2>/dev/null
                '''
                // Send emails only if not started by upstream (qat pipeline)
                if (!BUILD_CAUSE.contains("upstream")) {
                    emailext body:
                        "${BUILD_URL}",
                        recipientProviders: [[$class:'CulpritsRecipientProvider'],[$class:'RequesterRecipientProvider']],
                        subject: "${BUILD_TAG} - ${currentBuild.result}",
                        bcc: 'jerome.pioux@atos.net'
                }
            }
        } // always
    } // post
} // pipeline


// ---------------------------------------------------------------------------
//
// GROOVY FUNCTIONS
//
// ---------------------------------------------------------------------------
// Restore under $RUNTIME_DIR, the tarball containing $INSTALL_DIR of each
// dependency of this project depending on the stage we are in (build|test)
def restore_dependencies_install_dir() {
    def ARTIFACT_PROJECT_BRANCH = "/$BRANCH_NAME"
    if (JOB_BASE_NAME.contains(JOB_NAME)) {
        ARTIFACT_PROJECT_BRANCH=""
    }
    DEPENDENCIES = sh returnStdout: true, script: '''set +x
        echo -n "$($QATDIR/bin/get_dependencies.sh $STAGE_NAME $REPO_NAME tarballs_artifacts)"
    '''

    if (DEPENDENCIES?.trim()) {
        def filedeps = DEPENDENCIES
        if (!filedeps.isEmpty()) {
            filedeps.split('\n').each {
                if ((!it.isEmpty())) {
                    try {
                        env.REPO_DEPENDENT_NAME="${it}"
                        if (UI_RESTORE_ARTIFACT) {
                            copyArtifacts(filter: "${it}-*.tar.gz", projectName: "${it}.${OS}${ARTIFACT_PROJECT_BRANCH}", target: "tarballs_artifacts", fingerprintArtifacts: true, selector: buildParameter("$UI_RESTORE_ARTIFACT"))
                        } else {
                            copyArtifacts(filter: "${it}-*.tar.gz", projectName: "${it}.${OS}${ARTIFACT_PROJECT_BRANCH}", target: "tarballs_artifacts", fingerprintArtifacts: true)
                        }
                    } catch (error) {
                        echo "**** copyArtifacts: $error"
                        sh 'exit 1'
                    }
                    sh '''set +x
                        ls tarballs_artifacts/$REPO_DEPENDENT_NAME-*.tar.gz
                        mkdir -p $RUNTIME_DIR
                        tar xfz tarballs_artifacts/$REPO_DEPENDENT_NAME-*.tar.gz -C $RUNTIME_DIR
                        touch tarballs_artifacts/.$REPO_DEPENDENT_NAME.artifact
                    '''
                }
            }
        }
    }
}

