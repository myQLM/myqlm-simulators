#!/usr/local/bin/groovy

// ---------------------------------------------------------------------------
//
// GROOVY GLOBALS
//
// ---------------------------------------------------------------------------
def QLM_VERSION_FOR_DOCKER_IMAGE = "1.1.0"

// JOB_NAME:    qat-bdd | qat-bdd/master
// UI_OSVERSION:    7.8 | 8.2
// OS:              el7 | el8
// OSLABEL:     rhel7.8 | rhel8.2
// BRANCH_NAME:  master | rc

def LABEL = "master"

def OS
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

def OSLABEL  = "rhel$UI_OSVERSION"
if (!env.BRANCH_NAME) {
    env.BRANCH_NAME = "master"
}

HOST_NAME = InetAddress.getLocalHost().getHostName()

// Expose variables to bash and groovy functions
env.OS = "$OS"
env.HOST_NAME = "$HOST_NAME"
env.NIGHTLY_BUILD = params.NIGHTLY_BUILD


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
// Pipeline
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

        BLACK   = '\033[30m' ; B_BLACK   = '\033[1;30m'
        RED     = '\033[31m' ; B_RED     = '\033[1;31m'
        GREEN   = '\033[32m' ; B_GREEN   = '\033[1;32m'
        YELLOW  = '\033[33m' ; B_YELLOW  = '\033[1;33m'
        BLUE    = '\033[34m' ; B_BLUE    = '\033[1;34m'
        MAGENTA = '\033[35m' ; B_MAGENTA = '\033[1;35m'
        CYAN    = '\033[36m' ; B_CYAN    = '\033[1;36m'
        WHITE   = '\033[97m' ;B_WHITE   = '\033[1;37m'

        UNDERLINE = '\033[4m'
        RESET     = '\033[0m'

        BUILD_CAUSE      =  currentBuild.getBuildCauses()[0].shortDescription.toString()
        BUILD_CAUSE_NAME =  currentBuild.getBuildCauses()[0].userName.toString()

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

        QUALIFIED_REPO_NAME = sh returnStdout: true, script: '''set +x
            echo -n ${JOB_NAME%%/*}
        '''

        JOB_QUALIFIER = sh returnStdout: true, script: '''set +x
            JOB_QUALIFIER=${JOB_NAME#*-}
            JOB_QUALIFIER=${JOB_QUALIFIER#*-}
            n=${JOB_NAME//[^-]}
            if ((${#n} > 1)); then
                echo -n "/${JOB_QUALIFIER%%/*}"
            else
                echo -n "/"
            fi
        '''

        REPO_NAME = sh returnStdout: true, script: '''set +x
            if [[ ! $JOB_NAME =~ qat-functional-tests && \
                    $JOB_NAME =~ ^qat-.*-.*$ ]]; then
                JOB_NAME=${JOB_NAME%-*}
                if [[ $JOB_NAME =~ ^qat-.*-.*$ ]]; then
                    JOB_NAME=${JOB_NAME%-*}
                fi
            fi
            echo -n ${JOB_NAME%%/*}
        '''
    } 

    stages
    {
        stage("init") {
            steps {
                echo "${B_MAGENTA}[INIT]${RESET}"
                echo "\
BASEDIR             = ${BASEDIR}\n\
QATDIR              = ${QATDIR}\n\
QAT_REPO_BASEDIR    = ${QAT_REPO_BASEDIR}\n\
\n\
BUILD_CAUSE         = ${BUILD_CAUSE}\n\
BUILD_CAUSE_NAME    = ${BUILD_CAUSE_NAME}\n\
\n\
REPO_TYPE           = ${REPO_TYPE}\n\
NIGHTLY_BUILD       = ${NIGHTLY_BUILD}\n\
\n\
JOB_NAME            = ${JOB_NAME}\n\
QUALIFIED_REPO_NAME = ${QUALIFIED_REPO_NAME}\n\
JOB_QUALIFIER       = ${JOB_QUALIFIER}\n\
REPO_NAME           = ${REPO_NAME}\n\
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
                    if [[ ! $UI_PRODUCT =~ ^QLM$ || $JOB_QUALIFIER =~ client ]]; then
                        echo -e "--> Cloning cross-compilation, branch=$BRANCH_NAME  [$GIT_BASE_URL] ..."
                        cmd="git clone --single-branch --branch $BRANCH_NAME $GIT_BASE_URL/cross-compilation"
                        echo "> $cmd"
                        eval $cmd
                    fi
                '''
                script {
                    print "Loading build_methods functions ..."
                    build_methods           = load "${QATDIR}/jenkins/methods/build"
                    print "Loading install_methods functions ..."
                    install_methods         = load "${QATDIR}/jenkins/methods/install"
                    print "Loading internal_methods functions ..."
                    internal_methods        = load "${QATDIR}/jenkins/methods/internal"
                    print "Loading packaging_methods functions ..."
                    packaging_methods       = load "${QATDIR}/jenkins/methods/packaging"
                    print "Loading static_analysis_methods functions ..."
                    static_analysis_methods = load "${QATDIR}/jenkins/methods/static_analysis"
                    print "Loading test_methods functions ..."
                    test_methods            = load "${QATDIR}/jenkins/methods/tests"
                    print "Loading support_methods functions ..."
                    support_methods         = load "${QATDIR}/jenkins/methods/support"

                    // Set a few badges for the build
                    support_methods.badges()
                } 
            }
        }

        stage("versioning") {
            steps {
                script {
                    support_methods.versioning()
                }
            } 
        }

        stage("EL7")
        {
            when {
                expression {
                    echo "${B_MAGENTA}********************* [[ EL7 ]] *********************${RESET}"
                    return internal_methods.doit("$UI_PRODUCT", "$QUALIFIED_REPO_NAME", "EL7")
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
                BUILD_DIR        = "build_${CURRENT_PLATFORM}_${CURRENT_OS}"
                RUNTIME_DIR      = "$WORKSPACE/runtime_${CURRENT_PLATFORM}_${CURRENT_OS}"
                INSTALL_DIR      = "$WORKSPACE/install_${CURRENT_PLATFORM}_${CURRENT_OS}"
            }
            stages
            { 
                stage("build") {
                    steps {
                        script {
                            env.stage = "build"
                            support_methods.restore_tarballs_dependencies(env.stage)
                            build_methods.build()
                            install_methods.install()
                        }
                    }
                }

                stage("rpm") {
                    when { expression { return internal_methods.doit("$UI_PRODUCT", "$QUALIFIED_REPO_NAME", "EL7", "$STAGE_NAME") } }
                    steps {
                        script {
                            packaging_methods.rpm()
                        }
                    }
                }

                stage("wheel") {
                    when { expression { return internal_methods.doit("$UI_PRODUCT", "$QUALIFIED_REPO_NAME", "EL7", "$STAGE_NAME") } }
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

        stage("EL8")
        {
            when {
                expression {
                    echo "${B_MAGENTA}********************* [[ EL8 ]] *********************${RESET}"
                    return internal_methods.doit("$UI_PRODUCT", "$QUALIFIED_REPO_NAME", "EL8")
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
                BUILD_DIR        = "build_${CURRENT_PLATFORM}_${CURRENT_OS}"
                RUNTIME_DIR      = "$WORKSPACE/runtime_${CURRENT_PLATFORM}_${CURRENT_OS}"
                INSTALL_DIR      = "$WORKSPACE/install_${CURRENT_PLATFORM}_${CURRENT_OS}"
            }
            stages {
	        stage("linguist") {
                    steps {
                        script {
                            support_methods.linguist()
                        }
                    }
                }

                stage("build") {
                    steps {
                        script {
                            env.stage = "build"
                            support_methods.restore_tarballs_dependencies(env.stage)
                            build_methods.build()
                            install_methods.install()
                        }
                    }
                }

                stage("build-profiling") {
                    when {
                        allOf {
                            expression { if (env.UI_TESTS.toLowerCase().contains("with code coverage")) { return true } else { return false } };
                            expression { return internal_methods.doit("$UI_PRODUCT", "$QUALIFIED_REPO_NAME", "EL8", "$STAGE_NAME") }
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

                stage("rpm") {
                    when { expression { return internal_methods.doit("$UI_PRODUCT", "$QUALIFIED_REPO_NAME", "EL8", "$STAGE_NAME") } }
                    steps {
                        script {
                            packaging_methods.rpm()
                        }
                    }
                }

                stage("wheel") {
                    when { expression { return internal_methods.doit("$UI_PRODUCT", "$QUALIFIED_REPO_NAME", "EL8", "$STAGE_NAME") } }
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

        stage("CROSS-COMPILATION")
        {
            when {
                expression {
                    echo "${B_MAGENTA}********************* [[ CROSS-COMPILATION ]] *********************${RESET}"
                    return internal_methods.doit("$UI_PRODUCT", "$QUALIFIED_REPO_NAME", "CROSS-COMPILATION")
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
                RUNTIME_DIR      = "$WORKSPACE/runtime_${CURRENT_PLATFORM}_${CURRENT_OS}"
                MYQLM_PLATFORM   = "WIN_64"
                BUILD_DIR        = "build-${MYQLM_PLATFORM}"
                INSTALL_DIR      = "$WORKSPACE/install_${CURRENT_PLATFORM}_${CURRENT_OS}"
            }
            stages {
                stage("build") {
                    steps {
                        script {
                            env.stage = "build"
                            support_methods.restore_tarballs_dependencies(env.stage)
                            build_methods.build_cross_compilation()
                            install_methods.install_cross_compilation()
                        }
                    }
                }

                stage("wheel") {
                    when { expression { return internal_methods.doit("$UI_PRODUCT", "$QUALIFIED_REPO_NAME", "CROSS-COMPILATION", "$STAGE_NAME") } }
                    steps {
                        script {
                            packaging_methods.wheel_cross_compilation()
                        }
                    }
                }
            }
        }

        stage("STATIC-ANALYSIS")
        {
            when {
                expression {
                    echo "${B_MAGENTA}********************* [[ STATIC-ANALYSIS ]] *********************${RESET}"
                    return internal_methods.doit("$UI_PRODUCT", "$QUALIFIED_REPO_NAME", "STATIC-ANALYSIS")
                }
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
                RUNTIME_DIR      = "$WORKSPACE/runtime_${CURRENT_PLATFORM}_${CURRENT_OS}"
            }
            stages {
                stage("static-analysis") {
                    environment {
                        BUILD_DIR = "build_${CURRENT_PLATFORM}_${CURRENT_OS}"
                    }
                    parallel
                    {
                        stage("cppcheck") {
                            when { expression { return internal_methods.doit("$UI_PRODUCT", "$QUALIFIED_REPO_NAME", "STATIC-ANALYSIS", "$STAGE_NAME") } }
                            steps {
                                script {
                                    static_analysis_methods.cppcheck()
                                }
                            }
                        }
             
                        stage("pylint") {
                            when { expression { return internal_methods.doit("$UI_PRODUCT", "$QUALIFIED_REPO_NAME", "STATIC-ANALYSIS", "$STAGE_NAME") } }
                            steps {
                                script {
                                    static_analysis_methods.pylint()
                                }
                            }
                        }
    
                        stage("flake8") {
                            when { expression { return internal_methods.doit("$UI_PRODUCT", "$QUALIFIED_REPO_NAME", "STATIC-ANALYSIS", "$STAGE_NAME") } }
                            steps {
                                script {
                                    static_analysis_methods.flake8()
                                }
                            }
                        }
                    }
                }
            }
        }

        stage("UNIT-TESTS")
        {
            when {
                expression {
                    echo "${B_MAGENTA}********************* [[ UNIT-TESTS ]] *********************${RESET}"
                    return internal_methods.doit("$UI_PRODUCT", "$QUALIFIED_REPO_NAME", "UNIT-TESTS")
                }
                beforeAgent true
            }
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
                RUNTIME_DIR      = "$WORKSPACE/runtime_${CURRENT_PLATFORM}_${CURRENT_OS}"
            }
            stages {
                stage("tests") {
                    when { 
                        allOf {
                            expression { if (env.UI_TESTS.toLowerCase().contains("with code coverage")) { return false } else { return true } };
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
                            env.stage = "tests"
                            support_methods.restore_tarballs_dependencies(env.stage)
                            test_methods.tests()
                            test_methods.tests_reporting()
                        }
                    }
                }
     
                stage("tests-with-code-coverage") {
                    when { 
                        allOf {
                            expression { if (env.UI_TESTS.toLowerCase().contains("with code coverage")) { return true } else { return false } };
                            expression { return internal_methods.doit("$UI_PRODUCT", "$QUALIFIED_REPO_NAME", "UNIT-TESTS", "$STAGE_NAME") }
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
                            env.stage = "tests"
                            support_methods.restore_tarballs_dependencies(env.stage)
                            test_methods.tests_with_code_coverage()
                            test_methods.tests_reporting()
                        }
                    }
                }
            }
        }
    } // stages

    post
    {
        success {
            echo "${B_MAGENTA}[POST:success]${RESET}"
            script {
                sh '''set +x
                    rm -f tarballs_artifacts/.*.artifact 2>/dev/null
                '''
            }
        } // success

        always {
            echo "${B_MAGENTA}[POST:always]${RESET}"
            script {
                // Send emails only if not started by upstream (qat pipeline)
                if (!BUILD_CAUSE.contains("upstream")) {
                    emailext body: "${BUILD_URL}",
                        recipientProviders: [[$class:'CulpritsRecipientProvider'],[$class:'RequesterRecipientProvider']],
                        subject: "${BUILD_TAG} - ${currentBuild.result}"
                }
            }
        }
    } // post
} // pipeline

