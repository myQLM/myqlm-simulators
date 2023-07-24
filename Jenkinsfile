#!/usr/local/bin/groovy
/* groovylint-disable CatchException, CompileStatic */

/*
* Authors:     Atos BDS R&D CI/CD QLM Team
* Copyright:   2017-2023  Bull S.A.S. - All rights reserved.
*              This is not Free or Open Source software.
*              Please contact Bull SAS for details about its license.
*              Bull - Rue Jean Jaurès - B.P. 68 - 78340 Les Clayes-sous-Bois
* Description: Explicitly load our shared-libraries, then call the main Jenkinsfile
*              Limitation: We do not support branches others than master or rc for
*              the shared-libraries (IMHO, because of a Jenkins shortcoming).
*/

if (BRANCH_NAME == 'rc') {
    library 'ci@rc'
    library 'qat@rc'
    library 'qlmtools@rc'
} else {
    library 'ci@master'
    library 'qat@master'
    library 'qlmtools@master'
}

jenkinsfile('myqlm-simulators')
