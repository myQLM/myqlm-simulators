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
    echo "***** UI_OSVERSION undefined; setting it to 8.3 *****"
    UI_OSVERSION = 8.3
}

// Exception: staticMethod java.net.InetAddress getLocalHost
// Exception:       method java.net.InetAddress getHostName
HOST_NAME     = InetAddress.getLocalHost().getHostName()
env.HOST_NAME = "$HOST_NAME"

if (HOST_NAME.equals("qlmci.usrnd.lan"))
    LICENSE = "/etc/qlm/license_nogpu"
else
    LICENSE = "/etc/qlm/license"

env.US_PRODUCT_NAME    = params.DS_PRODUCT_NAME
env.US_PRODUCT_VERSION = params.DS_PRODUCT_VERSION
env.US_BUILD_DATE      = params.DS_BUILD_DATE
env.US_NIGHTLY_BUILD   = params.DS_NIGHTLY_BUILD

env.BUILD_CAUSE      = currentBuild.getBuildCauses()[0].shortDescription.toString()
env.BUILD_CAUSE_NAME = currentBuild.getBuildCauses()[0].userName.toString()

/* PARAMETERS
UI_PROJECT_VERSION
UI_OSVERSION        <- Upstream
UI_VERBOSE
UI_TESTS            <- Upstream
*/


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
    //pipelineTriggers([pollSCM('')]),
    parameters([
        [$class: 'ChoiceParameter', choiceType: 'PT_SINGLE_SELECT', description: '', filterLength: 1, filterable: false, name: 'UI_PROJECT_VERSION', randomName: 'choice-parameter-266216487624196',
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
                        return ['7.8', '8.2' ,'8.3:selected']
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
        _ = sh returnStdout: false, script: '''set +x
            git_base_url=ssh://bitbucketbdsfr.fsc.atos-services.net:7999/brq
            if [[ $HOST_NAME =~ qlmci2 ]]; then
                git_base_url=ssh://qlmjenkins@qlmgit.usrnd.lan:29418/qlm
            fi
            git_base_url_qat=${git_base_url}ext
            git clone --single-branch --branch master $git_base_url/ci _ci
            git clone --single-branch --branch master $git_base_url_qat/qat _qat
        '''

        RUN_BY_JENKINS = 1

        BASEDIR          = "$WORKSPACE"
        CIDIR            = "$BASEDIR/ci"
        QATDIR           = "$BASEDIR/qat"
        QAT_REPO_BASEDIR = "$BASEDIR"

        BLACK     = '\033[30m' ; B_BLACK   = '\033[1;30m'
        RED       = '\033[31m' ; B_RED     = '\033[1;31m'
        GREEN     = '\033[32m' ; B_GREEN   = '\033[1;32m'
        YELLOW    = '\033[33m' ; B_YELLOW  = '\033[1;33m'
        BLUE      = '\033[34m' ; B_BLUE    = '\033[1;34m'
        MAGENTA   = '\033[35m' ; B_MAGENTA = '\033[1;35m'
        CYAN      = '\033[36m' ; B_CYAN    = '\033[1;36m'
        WHITE     = '\033[97m' ; B_WHITE   = '\033[1;37m'
        UNDERLINE = '\033[4m'
        RESET     = '\033[0m'

        OSLABEL                     = "rhel$UI_OSVERSION"
        PY_VERSION                  = "py36"
        OSLABEL_CROSS_COMPILATION   = "rhel8.3"
        OS_CROSS_COMPILATION        = "el8"

        OSVERSION                   = "${UI_OSVERSION}"
        TESTS                       = "${UI_TESTS}"

        OS                          = get_os()
        REPO_NAME                   = get_repo_name(JOB_NAME)
        JOB_QUALIFIER               = get_job_qualifier(JOB_NAME)
        JOB_QUALIFIER_PATH          = get_job_qualifier_path(JOB_NAME)
        PRODUCT_NAME                = get_product_name(JOB_NAME)
        PROJECT_NAME                = get_project_name(JOB_NAME)
        PRODUCT_VERSION             = get_product_version(JOB_NAME)
        PROJECT_VERSION             = get_project_version(JOB_NAME)
        BUILD_VERSION               = get_build_version(JOB_NAME, BRANCH_NAME, BUILD_NUMBER)
        BUILD_DATE                  = get_build_date(HOST_NAME)
        RPM_RELEASE                 = get_rpm_release(JOB_NAME, BRANCH_NAME, HOST_NAME)
        BUILD_TYPE                  = get_build_type(BRANCH_NAME)
        REPO_TYPE                   = get_repo_type(BUILD_CAUSE, BRANCH_NAME)
        VERBOSE                     = get_verbose()
        NIGHTLY_BUILD               = get_nightly_build()
    }

    stages
    {
        stage("init")
        {
            steps {
                script {
                    display_environment_variables()
                    sh '''set +x
                        mkdir -p $REPO_NAME
                        shopt -s extglob dotglob
                        mv -- !(_ci|_qat) $REPO_NAME/ 2>/dev/null || true
                        mv _ci ci; mv _qat qat

                        # Clone cross compilation if needed
                        $WORKSPACE/ci/bin/clone_cross_compilation.sh $CIDIR $PROJECT_NAME
                    '''

                    print "Loading build functions           ..."; build           = load "${CIDIR}/methods/build.groovy"
                    print "Loading install functions         ..."; install         = load "${CIDIR}/methods/install.groovy"
                    print "Loading internal functions        ..."; internal        = load "${CIDIR}/methods/internal.groovy"
                    print "Loading packaging functions       ..."; packaging       = load "${CIDIR}/methods/packaging.groovy"
                    print "Loading static_analysis functions ..."; static_analysis = load "${CIDIR}/methods/static_analysis.groovy"
                    print "Loading support functions         ..."; support         = load "${CIDIR}/methods/support.groovy"
                    print "Loading test functions            ..."; test            = load "${CIDIR}/methods/tests.groovy"

                    // Set a few badges for the build
                    support.badges()

                    // Do not check for semaphore if the job was started from upstream (main) to avoid a deadlock
                    if (!BUILD_CAUSE_NAME.contains("null")) {
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
                    return internal.doit("$PROJECT_NAME", "BUILD36")
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
                    when { expression { return internal.doit("$PROJECT_NAME", "BUILD36", "$STAGE_NAME") } }
                    steps {
                        script {
                            support.linguist()
                        }
                    }
                }

                stage("build") {
                    when { expression { return internal.doit("$PROJECT_NAME", "BUILD36", "$STAGE_NAME") } }
                    steps {
                        script {
                            build.build("${env.STAGE_NAME}", "${env.OS}")
                        }
                    }
                }

                stage("install") {
                    when { expression { return internal.doit("$PROJECT_NAME", "BUILD36", "$STAGE_NAME") } }
                    steps {
                        script {
                            install.install("${env.OS}")
                        }
                    }
                }

                stage("rpm") {
                    when { expression { return internal.doit("$PROJECT_NAME", "BUILD36", "$STAGE_NAME") } }
                    steps {
                        script {
                            packaging.build_rpms()
                        }
                    }
                }

                stage("wheel") {
                    when { expression { return internal.doit("$PROJECT_NAME", "BUILD36", "$STAGE_NAME") } }
                    steps {
                        script {
                            packaging.build_wheels("${env.OS}")
                        }
                    }
                }

                stage("build_profiling") {
                    when {
                        allOf {
                            expression { if (env.TESTS.toLowerCase().contains("with code coverage")) { return true } else { return false } };
                            expression { return internal.doit("$PROJECT_NAME", "BUILD36", "$STAGE_NAME") }
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
                    return internal.doit("$PROJECT_NAME", "BUILD38")
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
                    when { expression { return internal.doit("$PROJECT_NAME", "BUILD38", "$STAGE_NAME") } }
                    steps {
                        script {
                            build.build("${env.STAGE_NAME}", "${env.OS}")
                        }
                    }
                }

                stage("install") {
                    when { expression { return internal.doit("$PROJECT_NAME", "BUILD38", "$STAGE_NAME") } }
                    steps {
                        script {
                            install.install("${env.OS}")
                        }
                    }
                }

                stage("wheel") {
                    when { expression { return internal.doit("$PROJECT_NAME", "BUILD38", "$STAGE_NAME") } }
                    steps {
                        script {
                            packaging.build_wheels("${env.OS}")
                        }
                    }
                }
            }
        }

        stage("CROSS_COMPILATION")
        {
            when {
                expression {
                    echo "${B_MAGENTA}"; echo "END SECTION"; echo "BEGIN SECTION: CROSS_COMPILATION"; echo "${RESET}"
                    return internal.doit("$PROJECT_NAME", "CROSS_COMPILATION")
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
                    when { expression { return internal.doit("$PROJECT_NAME", "CROSS_COMPILATION", "$STAGE_NAME") } }
                    steps {
                        script {
                            packaging.wheel_cross_compilation("${env.OS}")
                        }
                    }
                }
            }
        }

        stage("STATIC_ANALYSIS")
        {
            when {
                expression {
                    echo "${B_MAGENTA}"; echo "END SECTION"; echo "BEGIN SECTION: STATIC_ANALYSIS"; echo "${RESET}"
                    return internal.doit("$PROJECT_NAME", "STATIC_ANALYSIS")
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
                stage("static_analysis")
                {
                    parallel
                    {
                        stage("cppcheck") {
                            when { expression { return internal.doit("$PROJECT_NAME", "STATIC_ANALYSIS", "$STAGE_NAME") } }
                            steps {
                                script {
                                    static_analysis.cppcheck()
                                }
                            }
                        }

                        stage("pylint") {
                            when { expression { return internal.doit("$PROJECT_NAME", "STATIC_ANALYSIS", "$STAGE_NAME") } }
                            steps {
                                script {
                                    static_analysis.pylint()
                                }
                            }
                        }

                        stage("flake8") {
                            when { expression { return internal.doit("$PROJECT_NAME", "STATIC_ANALYSIS", "$STAGE_NAME") } }
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

        stage("UNIT_TESTS")
        {
            when {
                allOf {
                    expression {
                        echo "${B_MAGENTA}"; echo "END SECTION"; echo "BEGIN SECTION: UNIT_TESTS"; echo "${RESET}"
                        if (env.TESTS.toLowerCase().contains("skip")) { return false } else { return true }
                    };
                    expression { return internal.doit("$PROJECT_NAME", "UNIT_TESTS") }
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
                stage("unit_tests") {
                    when {
                        expression {
                            echo "${B_MAGENTA}--------------------- [[ UNIT_TESTS ]] ---------------------${RESET}"
                            return internal.doit("$PROJECT_NAME", "UNIT_TESTS", "UNIT_TESTS")
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

                stage("unit_tests_gpu")
                {
                    when {
                        allOf {
                            expression {
                                echo "${B_MAGENTA}--------------------- [[ UNIT_TESTS_GPU ]] ---------------------${RESET}"
                                return internal.doit("$PROJECT_NAME", "UNIT_TESTS", "UNIT_TESTS_GPU")
                            };
                            expression {
                                if (HOST_NAME.contains("qlmci2"))
                                    return false
                                return true
                            }
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

                stage("unit_tests_reporting")
                {
                    when {
                        expression {
                            echo "${B_MAGENTA}--------------------- [[ UNIT_TESTS_REPORTING ]] ---------------------${RESET}"
                            return internal.doit("$PROJECT_NAME", "UNIT_TESTS", "UNIT_TESTS_REPORTING")
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
            echo "\nEND SECTION\n[POST:always]"
        }

        success
        {
            echo "${B_MAGENTA}\n[POST:success]${RESET}"
            script {
                packaging.publish_rpms("success")
                packaging.publish_wheels("success")
                sh '''set +x
                    rm -f tarballs_artifacts/.*.artifact 2>/dev/null
                '''
                support.badges("post")
            }
        }

        unstable
        {
            echo "${B_MAGENTA}\n[POST:unstable]${RESET}"
            script {
                packaging.publish_rpms("unstable")
                packaging.publish_wheels("unstable")
                support.badges("post")
            }
        }

        cleanup
        {
            script {
                if (!BUILD_CAUSE.contains("upstream")) {        // Send emails only if not started by upstream (main)
                    emailext body: "${BUILD_URL}",
                        recipientProviders: [[$class:'CulpritsRecipientProvider'],[$class:'RequesterRecipientProvider']],
                        subject: "${BUILD_TAG} - ${currentBuild.result}"
                }
            }
        }
    } // post
} // pipeline


/*
-----------------------------------------------------------------------------------------------------------
GETTER FUNCTIONS
-----------------------------------------------------------------------------------------------------------
*/

/*
GET_REPO_NAME
*/
def get_repo_name(job_name)
{
    def reponames = [
        [project_name:"qat-tutorial-qlm",         repo_name:"qat-tutorial"],
        [project_name:"qat-tutorial-myqlm",       repo_name:"qat-tutorial"],
        [project_name:"qat-tutorial-qlmaas",      repo_name:"qat-tutorial"],
        [project_name:"qat-qlmaas-client",        repo_name:"qat-qlmaas"],
        [project_name:"qat-qlmaas-server-common", repo_name:"qat-qlmaas"],
        [project_name:"qat-qlmaas-server-django", repo_name:"qat-qlmaas"],
        [project_name:"qat-qlmaas-server-qlm",    repo_name:"qat-qlmaas"]
    ]

    def project_name = get_project_name(job_name)

    //reponames.each {entry -> println "$entry.project_name: $entry.repo_name"}
    def repo_name = reponames.find { it.project_name == "$project_name" }?.repo_name
    if (repo_name)
        return repo_name
    else
        return project_name
}

/*
GET_JOB_QUALIFIER
*/
def get_job_qualifier(job_name)
{
    def project_name = get_project_name(job_name)

    if (project_name.count('-') <= 1)
        return "-"
 
    c = project_name.indexOf('-', 4)        // Start after xxx-
    return project_name.substring(c+1).replaceAll('/','-')
}

/*
GET_JOB_QUALIFIER_PATH
*/
def get_job_qualifier_path(job_name)
{
    def job_qualifier_with_dashes = get_job_qualifier(job_name)
    job_qualifier_with_slashes = job_qualifier_with_dashes.replaceAll('-','/')
    if (! job_qualifier_with_slashes.startsWith('/'))
        job_qualifier_with_slashes = "/${job_qualifier_with_slashes}"
    return job_qualifier_with_slashes
}

/*
GET_PRODUCT_NAME
*/
def get_product_name(job_name) 
{
    if (! US_PRODUCT_NAME.equals("null"))
        return US_PRODUCT_NAME.toLowerCase()   // all

    def product_name
    if (job_name.contains("myqlm"))
        product_name = "myqlm"
    else if (job_name.contains("qlmaas"))
        product_name = "qlmaas"
    else
        product_name = "qlm"
    return product_name
}

/*
GET_PROJECT_NAME
*/
def get_project_name(job_name)
{
    def job_name_with_branch = job_name.tokenize('/') as String[]
    return job_name_with_branch[0]
}

/*
GET_PRODUCT_VERSION
*/
def get_product_version(job_name) 
{
    if (! US_PRODUCT_VERSION.equals("null"))
        return US_PRODUCT_VERSION

    def product_name = get_product_name(job_name)
    def product_version = new File("$WORKSPACE/_ci/share/versions/${product_name}.version").text
    return product_version
}

/*
GET_PROJECT_VERSION
*/
def get_project_version(job_name) 
{
    if (! UI_PROJECT_VERSION.equals("null"))
        return UI_PROJECT_VERSION

    def project_name = get_project_name(job_name)
    def project_version = new File("$WORKSPACE/_qat/share/versions/${project_name}.version").text
    return project_version
}

/*
GET_BUILD_VERSION
*/
def get_build_version(job_name, branch_name, build_number)
{
    def project_version = get_project_version(job_name)
    def build_version = project_version 
    if (! branch_name.equals("rc"))
        build_version = project_version + "." + build_number
    return build_version
}

/*
GET_BUILD_DATE
*/
def get_build_date(hostname)
{
    if (! US_BUILD_DATE.equals("null"))
        return US_BUILD_DATE

    def tz
    if (hostname.contains("qlmci2"))
        tz = TimeZone.getTimeZone("America/Phoenix")
    else
        tz = TimeZone.getTimeZone("Europe/Paris")
    return new Date().format("yyMMdd.HHmm", tz)
}

/*
GET_RPM_RELEASE
*/
def get_rpm_release(job_name, branch_name, hostname)
{
    def rpm_release
    if (branch_name.equals("rc"))
        rpm_release = "bull" + "." + get_product_version(job_name)
    else
        rpm_release = "bull" + "." + get_build_date(hostname)
    return rpm_release
}

/*
GET_BUILD_TYPE
*/
def get_build_type(branch_name)
{
    def build_type
    if (branch_name.equals("rc"))
        build_type = "release"
    else
        build_type = "debug"
    return build_type

}

/*
GET_REPO_TYPE
*/
def get_repo_type(build_cause, branch_name)
{
    def repo_type = "dev"
    if (build_cause.equals("upstream"))
        if (branch_name.equals("rc"))
            build_type = "rc"
        else
            build_type = "mls"
    return repo_type

}

/*
GET_VERBOSE
*/
def get_verbose()
{
    if (UI_VERBOSE)
        if (UI_VERBOSE.equals("true"))
            return "true"
        else
            return "false"
    else
        return "false"
}

/*
GET_NIGHTLY_BUILD
*/
def get_nightly_build()
{
    if (! US_NIGHTLY_BUILD.equals("null"))
        return US_NIGHTLY_BUILD
    return "false"
}

/*
GET_OS
*/
def get_os()
{
    if (UI_OSVERSION.startsWith("7."))
        return "el7"
    else if (UI_OSVERSION.startsWith("8."))
        return "el8"
    else if (UI_OSVERSION.startsWith("9."))
        return "el9"
    return "elx"
}

/*
DISPLAY_ENVIRONMENT_VARIABLES
*/
def display_environment_variables()
{
    echo "${B_MAGENTA}[INIT]${RESET}"
    echo "\
JOB_NAME                    = ${JOB_NAME}\n\
WORKSPACE                   = ${WORKSPACE}\n\
BRANCH_NAME                 = ${BRANCH_NAME}\n\
HOST_NAME                   = ${HOST_NAME}\n\
\n\
OS                          = ${OS}\n\
OSLABEL                     = ${OSLABEL}\n\
PY_VERSION                  = ${PY_VERSION}\n\
OSLABEL_CROSS_COMPILATION   = ${OSLABEL_CROSS_COMPILATION}\n\
OS_CROSS_COMPILATION        = ${OS_CROSS_COMPILATION}\n\
\n\
UPSTREAM PARAMETERS\n\
-------------------\n\
US_PRODUCT_NAME             = ${US_PRODUCT_NAME}\n\
US_PRODUCT_VERSION          = ${US_PRODUCT_VERSION}\n\
US_BUILD_DATE               = ${US_BUILD_DATE}\n\
US_NIGHTLY_BUILD            = ${US_NIGHTLY_BUILD}\n\
\n\
THIS JOB PARAMETERS\n\
-------------------\n\
UI_PROJECT_VERSION          = ${UI_PROJECT_VERSION}\n\
UI_OSVERSION                = ${UI_OSVERSION}\n\
UI_VERBOSE                  = ${UI_VERBOSE}\n\
UI_TESTS                    = ${UI_TESTS}\n\
\n\
CONSOLIDATED VARIABLES\n\
----------------------\n\
PRODUCT_NAME                = ${PRODUCT_NAME}\n\
PRODUCT_VERSION             = ${PRODUCT_VERSION}\n\
BUILD_DATE                  = ${BUILD_DATE}\n\
OSVERSION                   = ${OSVERSION}\n\
TESTS                       = ${TESTS}\n\
VERBOSE                     = ${VERBOSE}\n\
NIGHTLY_BUILD               = ${NIGHTLY_BUILD}\n\
\n\
PROJECT_VERSION             = ${PROJECT_VERSION}\n\
RPM_RELEASE                 = ${RPM_RELEASE}\n\
BUILD_VERSION               = ${BUILD_VERSION}\n\
\n\
BUILD_CAUSE                 = ${BUILD_CAUSE}\n\
BUILD_CAUSE_NAME            = ${BUILD_CAUSE_NAME}\n\
\n\
REPO_TYPE                   = ${REPO_TYPE}\n\
REPO_NAME                   = ${REPO_NAME}\n\
PROJECT_NAME                = ${PROJECT_NAME}\n\
JOB_QUALIFIER               = ${JOB_QUALIFIER}\n\
JOB_QUALIFIER_PATH          = ${JOB_QUALIFIER_PATH}\n\
\n\
BASEDIR                     = ${BASEDIR}\n\
CIDIR                       = ${CIDIR}\n\
QATDIR                      = ${QATDIR}\n\
QAT_REPO_BASEDIR            = ${QAT_REPO_BASEDIR}\n\
\n\
"
}

