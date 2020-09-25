#!/usr/local/bin/groovy

// ---------------------------------------------------------------------------
//
// GROOVY GLOBALS
//
// ---------------------------------------------------------------------------
def QLM_VERSION_FOR_DOCKER_IMAGE = "1.1.0"

//def REFERENCE_DOCKER = "yes"
def REFERENCE_DOCKER = "no"

// JOB_NAME:    qat-bdd | qat-bdd/master
// UI_OSVERSION:    7.8 | 8.2
// OS:              el7 | el8
// OSLABEL:     rhel7.8 | rhel8.2
// BRANCH_NAME:  master | rc
def OS
def LABEL
def OSLABEL
def DOCKER_IMAGE

LABEL = "master"

try {
    if ("$UI_OSVERSION".startsWith("7"))
        OS = "el7"
    else if ("$UI_OSVERSION".startsWith("8"))
        OS = "el8"
} catch (e) {
    echo "***** UI_OSVERSION undefined; setting it to 8.2 *****"
    UI_OSVERSION = 8.2
    OS = "el8"
}

OSLABEL  = "rhel$UI_OSVERSION"
if (!env.BRANCH_NAME) {
    env.BRANCH_NAME = "master"
}

if ("$REFERENCE_DOCKER".contains("yes"))
    DOCKER_IMAGE = "qlm-reference-${QLM_VERSION_FOR_DOCKER_IMAGE}-${OSLABEL}:latest"
else
    DOCKER_IMAGE = "qlm-devel-${QLM_VERSION_FOR_DOCKER_IMAGE}-${OSLABEL}:latest"

DOCKER_IMAGE_el7 = "qlm-devel-${QLM_VERSION_FOR_DOCKER_IMAGE}-rhel7.8:latest"

HOST_NAME = InetAddress.getLocalHost().getHostName()

// Expose variables to bash and groovy functions
env.OS = "$OS"
env.HOST_NAME = "$HOST_NAME"
env.NIGHTLY_BUILD = params.NIGHTLY_BUILD

// Show the parameters
echo "\
JOB_NAME     = ${JOB_NAME}\n\
BRANCH_NAME  = ${BRANCH_NAME}\n\
JOB_BASE_NAME= ${JOB_BASE_NAME}\n\
UI_OSVERSION = ${UI_OSVERSION}\n\
OS           = ${OS}\n\
OSLABEL      = ${OSLABEL}\n\
DOCKER_IMAGE = ${DOCKER_IMAGE}\n\
HOST_NAME    = ${HOST_NAME}"


// ---------------------------------------------------------------------------
//
// Configure some of the job properties
//
// ---------------------------------------------------------------------------
properties([
    [$class: 'JiraProjectProperty'], 
    [$class: 'EnvInjectJobProperty',
        info: [
            loadFilesFromMaster: false,
            propertiesContent: '''
                someList=
            ''',
            secureGroovyScript: [
                classpath: [],
                sandbox: false,
                script: ''
            ]
        ],
        keepBuildVariables: true,
        keepJenkinsSystemVariables: true,
        on: true
    ],
    buildDiscarder(logRotator(artifactDaysToKeepStr: '', artifactNumToKeepStr: '10', daysToKeepStr: '', numToKeepStr: '50')), 
    disableConcurrentBuilds(), 
    pipelineTriggers([pollSCM('')]),
    parameters([
        [$class: 'ChoiceParameter', choiceType: 'PT_SINGLE_SELECT', description: '', filterLength: 1, filterable: false, name: 'UI_VERSION', randomName: 'choice-parameter-266216487624195',
            script: [
                $class: 'ScriptlerScript',
                parameters: [ 
                    [$class: 'org.biouno.unochoice.model.ScriptlerScriptParameter', name: 'job_name',    value: "${JOB_NAME}"],
                    [$class: 'org.biouno.unochoice.model.ScriptlerScriptParameter', name: 'host_name',   value: "${HOST_NAME}"],
                    [$class: 'org.biouno.unochoice.model.ScriptlerScriptParameter', name: 'branch_name', value: "${BRANCH_NAME}"]
                ],
                scriptlerScriptId: 'ReturnNextVersions.groovy'
            ]
        ], 
        [$class: 'ChoiceParameter', choiceType: 'PT_RADIO', description: '', filterLength: 1, filterable: false, name: 'UI_OSVERSION', randomName: 'choice-parameter-744322351209535',
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
                        return ['7.8', '8.2:selected']
                    '''
                ]
            ]
        ],
        [$class: 'ChoiceParameter', choiceType: 'PT_RADIO', description: '', filterLength: 1, filterable: false, name: 'UI_PRODUCT', randomName: 'choice-parameter-2765756439171963', 
            script: [
                $class: 'ScriptlerScript',
                parameters: [
                    [$class: 'org.biouno.unochoice.model.ScriptlerScriptParameter', name: 'job_name', value: "${JOB_NAME}"]
                ],
                scriptlerScriptId: 'selectProductsToBuild.groovy'
            ]
        ],
        [$class: 'ChoiceParameter', choiceType: 'PT_CHECKBOX', description: 'VERBOSE option for cmake', filterLength: 1, filterable: false, name: 'UI_VERBOSE', randomName: 'choice-parameter-2765756439171960', 
            script: [
                $class: 'GroovyScript', 
                fallbackScript: [
                    classpath: [],
                    sandbox: false, 
                    script: '''
                    '''
                ], 
                script: [
                    classpath: [],
                    sandbox: false,
                    script: '''
                        return ['']
                    '''
                ]
            ]
        ],
        [$class: 'CascadeChoiceParameter', choiceType: 'PT_RADIO', description: '', filterLength: 1, filterable: false, name: 'UI_TESTS', randomName: 'choice-parameter-851409291728428', 
            referencedParameters: 'UI_OSVERSION,BRANCH_NAME',
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
                        if ("$UI_OSVERSION".startsWith("7") || "$BRANCH_NAME".contains("rc"))
                            return ['Run tests:selected', 'Run tests with code coverage:disabled', 'Skip tests']
                        else
                            return ['Run tests:selected', 'Run tests with code coverage', 'Skip tests']
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
    agent any 

    options {
        ansiColor('xterm')
        timeout(time:30,unit:"MINUTES")
    }

    environment {
        RUN_BY_JENKINS=1

        BASEDIR           = "$WORKSPACE"
        QATDIR            = "$BASEDIR/qat"
        QAT_REPO_BASEDIR  = "$BASEDIR"

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
            if [[ $JOB_NAME =~ ^qat-.*-.*$ ]]; then
                JOB_NAME=${JOB_NAME%-*}
                if [[ $JOB_NAME =~ ^qat-.*-.*$ ]]; then
                    JOB_NAME=${JOB_NAME%-*}
                fi
            fi
            echo -n ${JOB_NAME%%/*}
        '''

        BUILD_TYPE = sh returnStdout: true, script: '''set +x
            if [[ $BRANCH_NAME = rc ]]; then
                echo -n release
            else
                echo -n debug
            fi
        '''

        REPO_TYPE = sh returnStdout: true, script: '''set +x
            if [[ $NIGHTLY_BUILD = true ]]; then
                echo -n mls
            else 
                if [[ $BRANCH_NAME = master ]]; then
                    echo -n dev
                else
                    echo -n rc
                fi
            fi
        '''

        JOB_QUALIFIER = sh returnStdout: true, script: '''set +x
            JOB_QUALIFIER=${JOB_NAME#*qat-}
            JOB_QUALIFIER=${JOB_QUALIFIER#*-}
            n=${JOB_NAME//[^-]}
            if ((${#n} > 1)); then
                echo -n "/${JOB_QUALIFIER%%/*}"
            else
                echo -n "/"
            fi
        '''

        QUALIFIED_REPO_NAME = sh returnStdout: true, script: '''set +x
            x=$JOB_NAME
            if [[ $JOB_NAME =~ ^qat-.*-.*$ ]]; then
                x=${JOB_NAME%-*}
                if [[ $x =~ ^qat-.*-.*$ ]]; then
                    x=${x%-*}
                fi
            fi
            REPO_NAME=${x%%/*}
            JOB_QUALIFIER=${JOB_NAME#*qat-}
            JOB_QUALIFIER=${JOB_QUALIFIER#*-}
            n=${JOB_NAME//[^-]}
            if ((${#n} > 1)); then
                JOB_QUALIFIER="${JOB_QUALIFIER%%/*}"
                echo -n "${REPO_NAME}-${JOB_QUALIFIER}"
            else
                echo -n "${REPO_NAME}"
            fi
        '''
    } 


    stages
    {
        stage('init')
        {
            steps {
                echo "${MAGENTA}${BOLD}[INIT]${RESET}"
                echo "\
BASEDIR             = ${BASEDIR}\n\
QATDIR              = ${QATDIR}\n\
QAT_REPO_BASEDIR    = ${QAT_REPO_BASEDIR}\n\
\n\
BUILD_CAUSE         = ${BUILD_CAUSE}\n\
BUILD_CAUSE_NAME    = ${BUILD_CAUSE_NAME}\n\
\n\
REPO_NAME           = ${REPO_NAME}\n\
REPO_TYPE           = ${REPO_TYPE}\n\
BUILD_TYPE          = ${BUILD_TYPE}\n\
\n\
JOB_QUALIFIER       = ${JOB_QUALIFIER}\n\
QUALIFIED_REPO_NAME = ${QUALIFIED_REPO_NAME}\n\
NIGHTLY_BUILD       = ${NIGHTLY_BUILD}\n\
"
                sh '''set +x
                    mkdir -p $REPO_NAME
                    mv * $REPO_NAME/ 2>/dev/null  || true
                    mv .* $REPO_NAME/ 2>/dev/null || true

                    GIT_BASE_URL=ssh://bitbucketbdsfr.fsc.atos-services.net:7999/brq
                    if [[ $HOST_NAME =~ qlmci2 ]]; then
                        GIT_BASE_URL=ssh://qlmjenkins@qlmgit.usrnd.lan:29418/qlm
                    fi

                    # Clone qat repo
                    echo -e "--> Cloning qat, branch=$BRANCH_NAME  [$GIT_BASE_URL] ..."
                    cmd="git clone --single-branch --branch $BRANCH_NAME $GIT_BASE_URL/qat"
                    echo "> $cmd"
                    eval $cmd

                    # Clone cross-compilation repo for myQLM
                    if [[ $UI_PRODUCT =~ ^(myQLM|All)$ || $JOB_QUALIFIER =~ client ]]; then
                        echo -e "--> Cloning cross-compilation, branch=$BRANCH_NAME  [$GIT_BASE_URL] ..."
                        cmd="git clone --single-branch --branch $BRANCH_NAME $GIT_BASE_URL/cross-compilation"
                        echo "> $cmd"
                        eval $cmd
                    fi
                '''
                script {
                    print "Loading groovy functions ..."
                    support_methods         = load "${QATDIR}/jenkins_methods/support"
                    build_methods           = load "${QATDIR}/jenkins_methods/build"
                    install_methods         = load "${QATDIR}/jenkins_methods/install"
                    static_analysis_methods = load "${QATDIR}/jenkins_methods/static_analysis"
                    test_methods            = load "${QATDIR}/jenkins_methods/tests"
                    packaging_methods       = load "${QATDIR}/jenkins_methods/packaging"

                    // Set a few badges for the build
                    support_methods.badges()
                } 
            }
        } // Init

        // versioning
        stage("versioning") {
            steps {
                script {
                    support_methods.versioning()
                }
            } 
        }

        stage("BUILD-AND-INSTALL-EL7") {
            when {
                expression {
                    if (env.UI_OSVERSION.contains("7.8")) {
                        return true
                    } else {
                        return false
                    }
                }
                beforeAgent true
            }
            agent {
                docker {
                    label "${LABEL}"
                    image "qlm-devel-${QLM_VERSION_FOR_DOCKER_IMAGE}-rhel7.8:latest"
                    args '-v /data/jenkins/.ssh:/data/jenkins/.ssh -v /etc/qat/license:/etc/qat/license -v/etc/qlm/license:/etc/qlm/license -v /opt/qlmtools:/opt/qlmtools'
                    alwaysPull false
                    reuseNode true
                } 
            }
            environment {
                CURRENT_OS       = "el7"
                CURRENT_PLATFORM = "linux" 
                DEPENDENCIES_OS  = "$CURRENT_OS"
                BUILD_DIR        = "build_${CURRENT_PLATFORM}_${CURRENT_OS}"
                RUNTIME_DIR      = "$WORKSPACE/runtime_${CURRENT_PLATFORM}_${CURRENT_OS}"
                INSTALL_DIR      = "$WORKSPACE/install_${CURRENT_PLATFORM}_${CURRENT_OS}"
            }
            stages
            { 
                stage('build')
                {
                    steps {
                        script {
                            env.stage = "build"
                            support_methods.restore_tarballs_dependencies(env.stage)
                            build_methods.build()
                            install_methods.install()
                        }
                    }
                }

                stage("rpm")
                {
                    when {
                        allOf {
                            expression { if (UI_PRODUCT.contains("myQLM")) { return false } else { return true } };
                            not { equals expected:'/client', actual: "${JOB_QUALIFIER}" }
                        }
                    }
                    steps {
                        script {
                            packaging_methods.rpm()
                        }
                    }
                }

                stage("wheel")
                {
                    when {
                        anyOf {
                            expression { if (UI_PRODUCT.startsWith("QLM")) { return false } else { return true } };
                            equals expected:'/client', actual: "${JOB_QUALIFIER}"
                        }
                    }
                    environment {
                        BUILD_DIR = "build_${CURRENT_PLATFORM}_${CURRENT_OS}"
                    }
                    steps {
                        script {
                            packaging_methods.wheel()
                        }
                    }
                }
            }
        }

        stage("BUILD-AND-INSTALL-EL8") {
            when {
                anyOf {
                    expression { if (UI_PRODUCT.startsWith("QLM"))     { return true } else { return false } };
                    expression { if (env.UI_OSVERSION.contains("8.2")) { return true } else { return false } }
                }
                beforeAgent true
            }
            agent {
                docker {
                    label "${LABEL}"
                    image "qlm-devel-${QLM_VERSION_FOR_DOCKER_IMAGE}-rhel8.2:latest"
                    args '-v /data/jenkins/.ssh:/data/jenkins/.ssh -v /etc/qat/license:/etc/qat/license -v/etc/qlm/license:/etc/qlm/license -v /opt/qlmtools:/opt/qlmtools'
                    alwaysPull false
                    reuseNode true
                } 
            }
            environment {
                CURRENT_OS       = "el8"
                CURRENT_PLATFORM = "linux" 
                DEPENDENCIES_OS  = "$CURRENT_OS"
                BUILD_DIR        = "build_${CURRENT_PLATFORM}_${CURRENT_OS}"
                RUNTIME_DIR      = "$WORKSPACE/runtime_${CURRENT_PLATFORM}_${CURRENT_OS}"
                INSTALL_DIR      = "$WORKSPACE/install_${CURRENT_PLATFORM}_${CURRENT_OS}"
            }
            stages {
	        stage("linguist")
                {
                    steps {
                        script {
                            support_methods.linguist()
                        }
                    }
                }

                stage('build')
                {
                    steps {
                        script {
                            env.stage = "build"
                            support_methods.restore_tarballs_dependencies(env.stage)
                            build_methods.build()
                            install_methods.install()
                        }
                    }
                }

                stage('build-profiling')
                {
                    when {
                        allOf {
                            expression { if (env.UI_TESTS.toLowerCase().contains("with code coverage")) { return true } else { return false } };
                            expression { if (env.JOB_NAME.startsWith("myqlm-")) { return false } else { return true } }
                        }
                    }
                    environment {
                        BUILD_DIR   = "build-profiling_${CURRENT_PLATFORM}_${CURRENT_OS}"
                        INSTALL_DIR = "$WORKSPACE/install-profiling_${CURRENT_PLATFORM}_${CURRENT_OS}"
                    }
                    steps {
                        script {
                            env.stage = "build"
                            support_methods.restore_tarballs_dependencies(env.stage)
                            build_methods.build_profiling()
                            install_methods.install_profiling()
                        }
                    }
                }

                stage("rpm")
                {
                    when {
                        allOf {
                            expression { if (UI_PRODUCT.startsWith("myQLM")) { return false } else { return true } };
                            not { equals expected:'/client', actual: "${JOB_QUALIFIER}" }
                        }
                    }
                    steps {
                        script {
                            packaging_methods.rpm()
                        }
                    }
                } // rpm

                stage("wheel")
                {
                    when {
                        anyOf {
                            expression { if (UI_PRODUCT.startsWith("QLM")) { return false } else { return true } };
                            equals expected:'/client', actual: "${JOB_QUALIFIER}"
                        }
                    }
                    environment {
                        BUILD_DIR = "build_${CURRENT_PLATFORM}_${CURRENT_OS}"
                    }
                    steps {
                        script {
                            packaging_methods.wheel()
                        }
                    }
                }
            }
        }

        stage("CROSS-COMPILATION") {
            when {
                anyOf {
                    allOf {
                        expression { if (UI_PRODUCT.startsWith("QLM"))  { return false } else { return true } };
                        expression { if (JOB_NAME.startsWith("myqlm-")) { return false } else { return true } }
                    };
                    equals expected:'/client', actual: "${JOB_QUALIFIER}"
                }
                beforeAgent true
            }
            agent {
                docker {
                    label "${LABEL}"
                    image "qlm-devel-${QLM_VERSION_FOR_DOCKER_IMAGE}-rhel8.2:latest"
                    args '-v /data/jenkins/.ssh:/data/jenkins/.ssh -v /etc/qat/license:/etc/qat/license -v/etc/qlm/license:/etc/qlm/license -v /opt/qlmtools:/opt/qlmtools'
                    alwaysPull false
                    reuseNode true
                }
            }
            environment {
                CURRENT_OS       = "el8"
                CURRENT_PLATFORM = "win64" 
                DEPENDENCIES_OS  = "$CURRENT_OS"
                RUNTIME_DIR      = "$WORKSPACE/runtime_${CURRENT_PLATFORM}_${CURRENT_OS}"
                MYQLM_PLATFORM   = "WIN_64"
                BUILD_DIR        = "build-${MYQLM_PLATFORM}"
                INSTALL_DIR      = "$WORKSPACE/install_${CURRENT_PLATFORM}_${CURRENT_OS}"
            }
            stages {
                stage('build-dependencies-cross-compilation')
                {
                    steps {
                        script {
                            env.stage = "build"
                            support_methods.restore_tarballs_dependencies(env.stage)
                            build_methods.build_cross_compilation()
                            install_methods.install_cross_compilation()
                        }
                    }
                }

                stage("wheel-cross-compilation")
                {
                    steps {
                        script {
                            packaging_methods.wheel_cross_compilation()
                        }
                    }
                } // wheel
            }
        }

        stage("STATIC-ANALYSIS") {
            agent {
                docker {
                    label "${LABEL}"
                    image "qlm-devel-${QLM_VERSION_FOR_DOCKER_IMAGE}-rhel8.2:latest"
                    args '-v /data/jenkins/.ssh:/data/jenkins/.ssh -v /etc/qat/license:/etc/qat/license -v/etc/qlm/license:/etc/qlm/license -v /opt/qlmtools:/opt/qlmtools'
                    alwaysPull false
                    reuseNode true
                } 
            }
            environment {
                CURRENT_OS       = "el8"
                CURRENT_PLATFORM = "linux" 
                DEPENDENCIES_OS  = "$CURRENT_OS"
                RUNTIME_DIR      = "$WORKSPACE/runtime_${CURRENT_PLATFORM}_${CURRENT_OS}"
            }
            stages {
                stage('static-analysis')
                {
                    environment {
                        BUILD_DIR = "build_${CURRENT_PLATFORM}_${CURRENT_OS}"
                    }
                    parallel
                    {
                        stage('cppcheck') 
                        {
                            steps {
                                script {
                                    static_analysis_methods.cppcheck()
                                }
                            }
                        } // Cppcheck
             
             
                        stage("pylint")
                        {
                            steps {
                                script {
                                    static_analysis_methods.pylint()
                                }
                            }
                        } // Pylint
    

                        stage("flake8")
                        {
                            steps {
                                script {
                                    static_analysis_methods.flake8()
                                }
                            }
                        } // Flake8
                    }
                } // static analysis
            }
        }

        stage("UNIT-TESTS") {
            agent {
                docker {
                    label "${LABEL}"
                    image "qlm-devel-${QLM_VERSION_FOR_DOCKER_IMAGE}-${OSLABEL}:latest"
                    args '-v /data/jenkins/.ssh:/data/jenkins/.ssh -v /etc/qat/license:/etc/qat/license -v/etc/qlm/license:/etc/qlm/license -v /opt/qlmtools:/opt/qlmtools'
                    alwaysPull false
                    reuseNode true
                } 
            }
            environment {
                CURRENT_OS       = "$OS"
                CURRENT_PLATFORM = "linux" 
                DEPENDENCIES_OS  = "$CURRENT_OS"
                RUNTIME_DIR      = "$WORKSPACE/runtime_${CURRENT_PLATFORM}_${CURRENT_OS}"
            }
            stages {
                stage('tests-dependencies') 
                {
                    when {
                        expression { if (env.UI_TESTS.toLowerCase().contains("skip")) { return false } else { return true } }
                    }
                    steps {
                        echo "${MAGENTA}${BOLD}[TESTS-DEPENDENCIES]${RESET}"
                        script {
                            env.stage = "tests"
                            support_methods.restore_tarballs_dependencies(env.stage)
                        }
                    }
                } // Tests-dependencies
     
                stage('tests')
                {
                    when { 
                        allOf {
                            expression { if (env.UI_TESTS.toLowerCase().contains("with code coverage")) { return false } else { return true } }
                            expression { if (env.UI_TESTS.toLowerCase().contains("skip"))               { return false } else { return true } }
                        }
                    }
                    environment {
                        BUILD_DIR                   = "build_${CURRENT_PLATFORM}_${CURRENT_OS}"
                        INSTALL_DIR                 = "$WORKSPACE/install_${CURRENT_PLATFORM}_${CURRENT_OS}"
                        TESTS_REPORTS_DIR           = "$REPO_NAME/$BUILD_DIR/tests/reports"     
                        TESTS_REPORTS_DIR_JUNIT     = "$TESTS_REPORTS_DIR/junit"
                        TESTS_REPORTS_DIR_GTEST     = "$TESTS_REPORTS_DIR/gtest"
                        TESTS_REPORTS_DIR_CUNIT     = "$TESTS_REPORTS_DIR/cunit"
                        GTEST_OUTPUT                = "xml:$WORKSPACE/$TESTS_REPORTS_DIR_GTEST/"
                        TESTS_REPORTS_DIR_VALGRIND  = "$TESTS_REPORTS_DIR/valgrind"
                        VALGRIND_ARGS               = "--fair-sched=no --child-silent-after-fork=yes --tool=memcheck --xml=yes --xml-file=$WORKSPACE/$TESTS_REPORTS_DIR_VALGRIND/report.xml --leak-check=full --show-leak-kinds=all --show-reachable=no --track-origins=yes --run-libc-freeres=no --gen-suppressions=all --suppressions=$QATDIR/share/misc/valgrind.supp"
                    }
                    steps {
                        script {
                            test_methods.tests()
                            test_methods.tests_reporting()
                        }
                    }
                } // tests
     
                stage('tests-with-code-coverage')
                {
                    when { 
                        allOf {
                            expression { if (env.UI_TESTS.toLowerCase().contains("with code coverage")) { return true } else { return false } };
                            expression { if (env.UI_OSVERSION.contains("8.2")) { return true } else { return false } }
                        }
                    }
                    environment {
                        BUILD_DIR                   = "build-profiling_${CURRENT_PLATFORM}_${CURRENT_OS}"
                        INSTALL_DIR                 = "$WORKSPACE/install-profiling_${CURRENT_PLATFORM}_${CURRENT_OS}"
                        TESTS_REPORTS_DIR           = "$REPO_NAME/${BUILD_DIR}/tests/reports"     
                        TESTS_REPORTS_DIR_JUNIT     = "$TESTS_REPORTS_DIR/junit"
                        TESTS_REPORTS_DIR_GTEST     = "$TESTS_REPORTS_DIR/gtest"
                        TESTS_REPORTS_DIR_CUNIT     = "$TESTS_REPORTS_DIR/cunit"
                        GTEST_OUTPUT                = "xml:$WORKSPACE/$TESTS_REPORTS_DIR_GTEST/"
                        TESTS_REPORTS_DIR_COVERAGE  = "$TESTS_REPORTS_DIR/coverage"
                        TESTS_REPORTS_DIR_COVERAGEPY= "$REPO_NAME/${BUILD_DIR}/tests/htmlcov"
                        TESTS_REPORTS_DIR_VALGRIND  = "$TESTS_REPORTS_DIR/valgrind"
                        VALGRIND_ARGS               = "--fair-sched=no --child-silent-after-fork=yes --tool=memcheck --xml=yes --xml-file=$WORKSPACE/$TESTS_REPORTS_DIR_VALGRIND/report.xml --leak-check=full --show-leak-kinds=all --show-reachable=no --track-origins=yes --run-libc-freeres=no --gen-suppressions=all --suppressions=$QATDIR/share/misc/valgrind.supp"
                    }
                    steps {
                        script {
                            test_methods.tests_with_code_coverage()
                            test_methods.tests_reporting()
                        }
                    }
                } // tests-with-code-coverage
            }
        }
    } // stages

    post
    {
        success
        {
            echo "${MAGENTA}${BOLD}[POST:success]${RESET}"
            script {
                sh '''set +x
                    rm -f tarballs_artifacts/.*.artifact 2>/dev/null
                '''
            }
        } // success

        always
        {
            echo "${MAGENTA}${BOLD}[POST:always]${RESET}"
            script {
                // Send emails only if not started by upstream (qat pipeline)
                if (!BUILD_CAUSE.contains("upstream")) {
                    emailext body: "${BUILD_URL}",
                        recipientProviders: [[$class:'CulpritsRecipientProvider'],[$class:'RequesterRecipientProvider']],
                        subject: "${BUILD_TAG} - ${currentBuild.result}"
                }
            }
        } // always
    } // post
} // pipeline

