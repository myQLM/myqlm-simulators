#!/usr/local/bin/groovy

// ---------------------------------------------------------------------------
//
// GROOVY GLOBALS
//
// ---------------------------------------------------------------------------
def QLM_VERSION_FOR_DOCKER_IMAGE = "1.2.1"

// Jenkins master/slave
def LABEL = "master"

try {   // Use on new jobs
    x = UI_OSVERSION
} catch (e) {
    echo "***** UI_OSVERSION undefined; setting it to 8.2 *****"
    UI_OSVERSION = 8.2
}

// Exception: staticMethod java.net.InetAddress getLocalHost
// Exception:       method java.net.InetAddress getHostName
HOST_NAME     = InetAddress.getLocalHost().getHostName()
env.HOST_NAME = "$HOST_NAME"

if (HOST_NAME.equals("qlmci.usrnd.lan"))
    LICENSE = "/etc/qlm/license_nogpu"
else
    LICENSE = "/etc/qlm/license"

// Expose params to bash
env.UI_PRODUCT      = params.UI_PRODUCT
env.PRODUCT_VERSION = params.UI_PRODUCT_VERSION
env.NIGHTLY_BUILD   = params.NIGHTLY_BUILD
env.MAIN_BUILD_DATE = params.MAIN_BUILD_DATE
env.BUILD_CAUSE     = currentBuild.getBuildCauses()[0].shortDescription.toString()


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
        [$class: 'ChoiceParameter', choiceType: 'PT_RADIO', description: '<br>', filterLength: 1, filterable: false, name: 'UI_PRODUCT', randomName: 'choice-parameter-266216487624195',
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
                        return ['QLM:selected', 'myQLM', 'QLMaaS']
                    '''
                ]
            ]
        ],
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

    options
    {
        ansiColor('xterm')
        timeout(time:90,unit:"MINUTES")     // Large enough to count for semaphore if main is running
    }

    environment
    {
        RUN_BY_JENKINS = 1

        BASEDIR          = "$WORKSPACE"
        CIDIR            = "$BASEDIR/ci"
        QATDIR           = "$BASEDIR/qat"
        QAT_REPO_BASEDIR = "$BASEDIR"

        BLACK   = '\033[30m' ; B_BLACK   = '\033[1;30m'
        RED     = '\033[31m' ; B_RED     = '\033[1;31m'
        GREEN   = '\033[32m' ; B_GREEN   = '\033[1;32m'
        YELLOW  = '\033[33m' ; B_YELLOW  = '\033[1;33m'
        BLUE    = '\033[34m' ; B_BLUE    = '\033[1;34m'
        MAGENTA = '\033[35m' ; B_MAGENTA = '\033[1;35m'
        CYAN    = '\033[36m' ; B_CYAN    = '\033[1;36m'
        WHITE   = '\033[97m' ; B_WHITE   = '\033[1;37m'

        UNDERLINE = '\033[4m'
        RESET     = '\033[0m'

        //BUILD_CAUSE      = currentBuild.getBuildCauses()[0].shortDescription.toString()
        BUILD_CAUSE_NAME = currentBuild.getBuildCauses()[0].userName.toString()

        OS = sh returnStdout: true, script: '''set +x
            if [[ $UI_OSVERSION =~ ^7 ]]; then
                echo -n "el7"
            else
                echo -n "el8"
            fi
        '''

        OSLABEL                   = "rhel$UI_OSVERSION"
        PY_VERSION                = "py36"

        OSLABEL_CROSS_COMPILATION = "rhel8.2"
        OS_CROSS_COMPILATION      = "el8"

        OSLABEL_UNIT_TESTS_2      = "rhel8.2"
        OS_UNIT_TESTS_2           = "el8"

        BUILD_TYPE = sh returnStdout: true, script: '''set +x
            build_type=debug
            [[ $BRANCH_NAME = rc ]] && build_type=release
            echo -n $build_type
        '''

        REPO_TYPE = sh returnStdout: true, script: '''set +x
            repo_type=dev
            if [[ $BUILD_CAUSE =~ upstream ]]; then
                if [[ $BRANCH_NAME = rc ]]; then
                    repo_type=rc
                else
                    repo_type=mls
                fi
            fi
            echo -n $repo_type
        '''

        QUALIFIED_REPO_NAME = sh returnStdout: true, script: '''set +x
            qualified_repo_name=${JOB_NAME%%/*}
            echo -n $qualified_repo_name
        '''

        JOB_QUALIFIER = sh returnStdout: true, script: '''set +x
            job_qualifier=${JOB_NAME#*-}
            job_qualifier=${job_qualifier#*-}
            n=${JOB_NAME//[^-]}
            if ((${#n} > 1)); then
                job_qualifier="${job_qualifier%%/*}"
            else
                job_qualifier='-'
            fi
            echo -n $job_qualifier
        '''

        JOB_QUALIFIER_PATH = sh returnStdout: true, script: '''set +x
            job_qualifier=${JOB_NAME#*-}
            job_qualifier=${job_qualifier#*-}
            n=${JOB_NAME//[^-]}
            if ((${#n} > 1)); then
                job_qualifier="/${job_qualifier%%/*}"
            else
                job_qualifier='-'
            fi
            job_qualifier_path="${job_qualifier//-//}"
            echo -n $job_qualifier_path
        '''

        REPO_NAME = sh returnStdout: true, script: '''set +x
            job_name=$JOB_NAME
            if [[ ! $job_name =~ qat-functional-tests && \
                    $job_name =~ ^qat-.*-.*$ ]]; then
                job_name=${job_name%-*}
                [[ $job_name =~ ^qat-.*-.*$ ]] && job_name=${job_name%-*}
            fi
            job_name=${job_name%%/*}
            echo -n $job_name
        '''

        BUILD_DATE = sh returnStdout: true, script: '''set +x
            if [[ $MAIN_BUILD_DATE != null ]]; then
                build_date=${MAIN_BUILD_DATE}
            else
                if [[ $HOST_NAME =~ qlmci2 ]]; then
                    build_date=$(TZ=America/Phoenix && date +"%y%m%d.%H%M")
                else
                    build_date=$(TZ=Europe/Paris && date +"%y%m%d.%H%M")
                fi
            fi
            echo -n $build_date
        '''

        PRODUCT_VERSION = sh returnStdout: true, script: '''set +x
            # Clone ci repo
            git_base_url=ssh://bitbucketbdsfr.fsc.atos-services.net:7999/brq
            if [[ $HOST_NAME =~ qlmci2 ]]; then
                git_base_url=ssh://qlmjenkins@qlmgit.usrnd.lan:29418/qlm
            fi
            git clone --single-branch --branch master $git_base_url/ci

            if [[ $PRODUCT_VERSION != null ]]; then
                product_version=${PRODUCT_VERSION}
            else
                product_version="$(cat $WORKSPACE/ci/share/versions/${UI_PRODUCT,,}.version)"
            fi
            echo -n $product_version
        '''

        PRODUCT_NAME = "$UI_PRODUCT"
    }

    stages
    {
        stage("init")
        {
            steps {
                echo "${B_MAGENTA}[INIT]${RESET}"
                echo "\
BASEDIR             = ${BASEDIR}\n\
CIDIR               = ${CIDIR}\n\
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
REPO_NAME           = ${REPO_NAME}\n\
QUALIFIED_REPO_NAME = ${QUALIFIED_REPO_NAME}\n\
JOB_QUALIFIER       = ${JOB_QUALIFIER}\n\
JOB_QUALIFIER_PATH  = ${JOB_QUALIFIER_PATH}\n\
\n\
BUILD_DATE          = ${BUILD_DATE}\n\
\n\
"
                sh '''set +x
                    mkdir -p $REPO_NAME
                    shopt -s extglob dotglob
                    mv -- !(ci) $REPO_NAME/ 2>/dev/null || true

                    git_base_url=ssh://bitbucketbdsfr.fsc.atos-services.net:7999/brq
                    if [[ $HOST_NAME =~ qlmci2 ]]; then
                        git_base_url=ssh://qlmjenkins@qlmgit.usrnd.lan:29418/qlm
                    fi

                    # Clone qat repo
                    git_base_url_qat=${git_base_url}ext
                    echo -e "\n--> Cloning qat, branch=master  [$git_base_url_qat] ..."
                    cmd="git clone --single-branch --branch master $git_base_url_qat/qat"
                    echo "> $cmd"
                    eval $cmd

                    ${CIDIR}/jenkins/scripts/checkout_cross_compilation.sh "$CIDIR" "$git_base_url" "$REPO_NAME"
                '''

                script {
                    print "Loading build functions           ..."; build           = load "${CIDIR}/jenkins/methods/build.groovy"
                    print "Loading install functions         ..."; install         = load "${CIDIR}/jenkins/methods/install.groovy"
                    print "Loading internal functions        ..."; internal        = load "${CIDIR}/jenkins/methods/internal.groovy"
                    print "Loading packaging functions       ..."; packaging       = load "${CIDIR}/jenkins/methods/packaging.groovy"
                    print "Loading static_analysis functions ..."; static_analysis = load "${CIDIR}/jenkins/methods/static_analysis.groovy"
                    print "Loading support functions         ..."; support         = load "${CIDIR}/jenkins/methods/support.groovy"
                    print "Loading test functions            ..."; test            = load "${CIDIR}/jenkins/methods/tests.groovy"

                    // Set a few badges for the build
                    support.badges()

                    // Do not check for semaphore if the job was started from upstream (main) to avoid a deadlock
                    if (!env.BUILD_CAUSE_NAME.contains("null")) {
                        lock('mainlock') {}
                    }
                }
            }
        }

        stage("versioning")
        {
            steps {
                script {
                    support.versioning()
                }
            }
        }

        stage("BUILD36")
        {
            when {
                expression {
                    echo "${B_MAGENTA}"; echo "END SECTION"; echo "BEGIN SECTION: BUILD36"; echo "${RESET}"
                    return internal.doit("$QUALIFIED_REPO_NAME", "BUILD36")
                }
                beforeAgent true
            }
            agent {
                docker {
                    label "${LABEL}"
                    image "qlm-${QLM_VERSION_FOR_DOCKER_IMAGE}-${OSLABEL}-${PY_VERSION}:latest"
                    args "-v /var/lib/jenkins/.ssh:/var/lib/jenkins/.ssh -v /etc/qat/license:/etc/qat/license -v$LICENSE:/etc/qlm/license -v /opt/qlmtools:/opt/qlmtools"
                    alwaysPull false
                    reuseNode true
                }
            }
            stages {
                stage("linguist") {
                    steps {
                        script {
                            support.linguist()
                        }
                    }
                }

                stage("build") {
                    when { expression { return internal.doit("$QUALIFIED_REPO_NAME", "BUILD36", "$STAGE_NAME") } }
                    steps {
                        script {
                            build.build("${env.STAGE_NAME}", "${env.OS}")
                            install.install("${env.OS}")
                        }
                    }
                }

                stage("rpm") {
                    when { expression { return internal.doit("$QUALIFIED_REPO_NAME", "BUILD36", "$STAGE_NAME") } }
                    steps {
                        script {
                            packaging.rpm()
                        }
                    }
                }

                stage("wheel") {
                    when { expression { return internal.doit("$QUALIFIED_REPO_NAME", "BUILD36", "$STAGE_NAME") } }
                    steps {
                        script {
                            packaging.wheel("${env.OS}")
                        }
                    }
                }

                stage("build-profiling") {
                    when {
                        allOf {
                            expression { if (env.UI_TESTS.toLowerCase().contains("with code coverage")) { return true } else { return false } };
                            expression { return internal.doit("$QUALIFIED_REPO_NAME", "BUILD36", "$STAGE_NAME") }
                        }
                    }
                    steps {
                        script {
                            build.build_profiling("${env.OS}")
                            install.install_profiling("${env.OS}")
                        }
                    }
                }
            }
        }


        stage("BUILD38")
        {
            when {
                expression {
                    echo "${B_MAGENTA}"; echo "END SECTION"; echo "BEGIN SECTION: BUILD38"; echo "${RESET}"
                    return internal.doit("$QUALIFIED_REPO_NAME", "BUILD38")
                }
                beforeAgent true
            }
            agent {
                docker {
                    label "${LABEL}"
                    image "qlm-${QLM_VERSION_FOR_DOCKER_IMAGE}-${OSLABEL_CROSS_COMPILATION}-py38:latest"
                    args "-v /var/lib/jenkins/.ssh:/var/lib/jenkins/.ssh -v /etc/qat/license:/etc/qat/license -v$LICENSE:/etc/qlm/license -v /opt/qlmtools:/opt/qlmtools"
                    alwaysPull false
                    reuseNode true
                }
            }
            stages {
                stage("build") {
                    when { expression { return internal.doit("$QUALIFIED_REPO_NAME", "BUILD38", "$STAGE_NAME") } }
                    steps {
                        script {
                            build.build("${env.STAGE_NAME}", "${env.OS}")
                            install.install("${env.OS}")
                        }
                    }
                }

                stage("wheel") {
                    when { expression { return internal.doit("$QUALIFIED_REPO_NAME", "BUILD38", "$STAGE_NAME") } }
                    steps {
                        script {
                            packaging.wheel("${env.OS}")
                        }
                    }
                }
            }
        }

        stage("CROSS-COMPILATION")
        {
            when {
                expression {
                    echo "${B_MAGENTA}"; echo "END SECTION"; echo "BEGIN SECTION: CROSS_COMPILATION"; echo "${RESET}"
                    return internal.doit("$QUALIFIED_REPO_NAME", "CROSS-COMPILATION")
                }
                beforeAgent true
            }
            agent {
                docker {
                    label "${LABEL}"
                    image "qlm-${QLM_VERSION_FOR_DOCKER_IMAGE}-${OSLABEL_CROSS_COMPILATION}-${PY_VERSION}:latest"
                    args "-v /var/lib/jenkins/.ssh:/var/lib/jenkins/.ssh -v /etc/qat/license:/etc/qat/license -v$LICENSE:/etc/qlm/license -v /opt/qlmtools:/opt/qlmtools"
                    alwaysPull false
                    reuseNode true
                }
            }
            stages {
                stage("build") {
                    steps {
                        script {
                            build.build_cross_compilation("${env.STAGE_NAME}", "${env.OS}")
                            install.install_cross_compilation("${env.OS}")
                        }
                    }
                }

                stage("wheel") {
                    when { expression { return internal.doit("$QUALIFIED_REPO_NAME", "CROSS-COMPILATION", "$STAGE_NAME") } }
                    steps {
                        script {
                            packaging.wheel_cross_compilation("${env.OS}")
                        }
                    }
                }
            }
        }

        stage("STATIC-ANALYSIS")
        {
            when {
                expression {
                    echo "${B_MAGENTA}"; echo "END SECTION"; echo "BEGIN SECTION: STATIC_ANALYSIS"; echo "${RESET}"
                    return internal.doit("$QUALIFIED_REPO_NAME", "STATIC-ANALYSIS")
                }
            }
            agent {
                docker {
                    label "${LABEL}"
                    image "qlm-${QLM_VERSION_FOR_DOCKER_IMAGE}-${OSLABEL}-${PY_VERSION}:latest"
                    args "-v /var/lib/jenkins/.ssh:/var/lib/jenkins/.ssh -v /etc/qat/license:/etc/qat/license -v$LICENSE:/etc/qlm/license -v /opt/qlmtools:/opt/qlmtools"
                    alwaysPull false
                    reuseNode true
                }
            }
            stages
            {
                stage("static-analysis")
                {
                    parallel
                    {
                        stage("cppcheck") {
                            when { expression { return internal.doit("$QUALIFIED_REPO_NAME", "STATIC-ANALYSIS", "$STAGE_NAME") } }
                            steps {
                                script {
                                    static_analysis.cppcheck()
                                }
                            }
                        }

                        stage("pylint") {
                            when { expression { return internal.doit("$QUALIFIED_REPO_NAME", "STATIC-ANALYSIS", "$STAGE_NAME") } }
                            steps {
                                script {
                                    static_analysis.pylint()
                                }
                            }
                        }

                        stage("flake8") {
                            when { expression { return internal.doit("$QUALIFIED_REPO_NAME", "STATIC-ANALYSIS", "$STAGE_NAME") } }
                            steps {
                                script {
                                    static_analysis.flake8()
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
                allOf {
                    expression {
                        echo "${B_MAGENTA}"; echo "END SECTION"; echo "BEGIN SECTION: UNIT_TESTS"; echo "${RESET}"
                        if (env.UI_TESTS.toLowerCase().contains("skip")) { return false } else { return true }
                    };
                    expression { return internal.doit("$QUALIFIED_REPO_NAME", "UNIT-TESTS") }
                }
            }
            environment {
                RUNTIME_DIR                  = "$WORKSPACE/runtime_linux_${env.OS}_python36"
                INSTALL_DIR                  = support.getenv("INSTALL_DIR", "linux", "${env.OS}", "python36")
                BUILD_DIR                    = support.getenv("BUILD_DIR",   "linux", "${env.OS}", "python36")
                TESTS_REPORTS_DIR            = "$REPO_NAME/$BUILD_DIR/tests/reports"
                TESTS_REPORTS_DIR_JUNIT      = "$TESTS_REPORTS_DIR/junit"
                TESTS_REPORTS_DIR_CUNIT      = "$TESTS_REPORTS_DIR/cunit"
                TESTS_REPORTS_DIR_GTEST      = "$TESTS_REPORTS_DIR/gtest"
                GTEST_OUTPUT                 = "xml:$WORKSPACE/$TESTS_REPORTS_DIR_GTEST/"
                TESTS_REPORTS_DIR_VALGRIND   = "$TESTS_REPORTS_DIR/valgrind"
                TESTS_REPORTS_DIR_COVERAGE   = "$TESTS_REPORTS_DIR/coverage"
                TESTS_REPORTS_DIR_COVERAGEPY = "$REPO_NAME/${BUILD_DIR}/tests/htmlcov"
                VALGRIND_ARGS                = "--fair-sched=no --child-silent-after-fork=yes --tool=memcheck --xml=yes --xml-file=$WORKSPACE/$TESTS_REPORTS_DIR_VALGRIND/report.xml --leak-check=full --show-leak-kinds=all --show-reachable=no --track-origins=yes --run-libc-freeres=no --gen-suppressions=all --suppressions=$QAT"
            }
            stages
            {
                stage("unit-tests") {
                    when {
                        expression {
                            echo "${B_MAGENTA}--------------------- [[ UNIT-TESTS ]] ---------------------${RESET}"
                            return internal.doit("$QUALIFIED_REPO_NAME", "UNIT-TESTS", "UNIT-TESTS")
                        }
                        beforeAgent true
                    }
                    agent {
                        docker {
                            label "${LABEL}"
                            image "qlm-${QLM_VERSION_FOR_DOCKER_IMAGE}-${OSLABEL}-${PY_VERSION}:latest"
                            args "-v /var/lib/jenkins/.ssh:/var/lib/jenkins/.ssh -v /etc/qat/license:/etc/qat/license -v$LICENSE:/etc/qlm/license -v /opt/qlmtools:/opt/qlmtools"
                            alwaysPull false
                            reuseNode true
                        }
                    }
                    steps {
                        script {
                            support.restore_dependencies_tarballs("$STAGE_NAME")
                            test.tests("$STAGE_NAME", "${env.OS}")
                        }
                    }
                }

                stage("unit-tests-gpu")
                {
                    when {
                        expression {
                            echo "${B_MAGENTA}--------------------- [[ UNIT-TESTS-GPU ]] ---------------------${RESET}"
                            return internal.doit("$QUALIFIED_REPO_NAME", "UNIT-TESTS", "UNIT-TESTS-GPU")
                        }
                        beforeAgent true
                    }
                    agent none
                    steps {
                        script {
                            support.restore_dependencies_tarballs("$STAGE_NAME")
                            test.tests("$STAGE_NAME", "${env.OS}")
                        }
                    }
                }

                stage("unit-tests-reporting")
                {
                    when {
                        expression {
                            echo "${B_MAGENTA}--------------------- [[ UNIT-TESTS-REPORTING ]] ---------------------${RESET}"
                            return internal.doit("$QUALIFIED_REPO_NAME", "UNIT-TESTS", "UNIT-TESTS-REPORTING")
                        }
                        beforeAgent true
                    }
                    agent {
                        docker {
                            label "${LABEL}"
                            image "qlm-${QLM_VERSION_FOR_DOCKER_IMAGE}-${OSLABEL}-${PY_VERSION}:latest"
                            args "-v /var/lib/jenkins/.ssh:/var/lib/jenkins/.ssh -v /etc/qat/license:/etc/qat/license -v$LICENSE:/etc/qlm/license -v /opt/qlmtools:/opt/qlmtools"
                            alwaysPull false
                            reuseNode true
                        }
                    }
                    steps {
                        script {
                            test.tests_reporting("$STAGE_NAME")
                        }
                    }
                }
            }
        }
    } // stages


    post
    {
        always
        {
            echo "${B_MAGENTA}\nEND SECTION\n[POST:always]${RESET}"
        }

        success
        {
            echo "${B_MAGENTA}\n[POST:success]${RESET}"
            script {
                sh '''set +x
                    ${CIDIR}/jenkins/scripts/publish_rpms.sh success
                    ${CIDIR}/jenkins/scripts/publish_wheels.sh success
                    rm -f tarballs_artifacts/.*.artifact 2>/dev/null
                '''
            }
        }

        unstable
        {
            echo "${B_MAGENTA}\n[POST:unstable]${RESET}"
            script {
                sh '''set +x
                    ${CIDIR}/jenkins/scripts/publish_rpms.sh unstable
                    ${CIDIR}/jenkins/scripts/publish_wheels.sh unstable
                '''
            }
        }

        cleanup
        {
            echo "${B_MAGENTA}[POST:cleanup]${RESET}"
            script {
                support.badges("post")
                if (!BUILD_CAUSE.contains("upstream")) {        // Send emails only if not started by upstream (main)
                    emailext body: "${BUILD_URL}",
                        recipientProviders: [[$class:'CulpritsRecipientProvider'],[$class:'RequesterRecipientProvider']],
                        subject: "${BUILD_TAG} - ${currentBuild.result}"
                }
            }
        }
    } // post
} // pipeline


