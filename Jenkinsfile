/*
* Authors:     Atos BDS R&D CI/CD Qaptiva Team
* Copyright:   2017-2025  Bull S.A.S. - All rights reserved.
*              This is not Free or Open Source software.
*              Please contact Bull SAS for details about its license.
*              Bull - Rue Jean Jaurès - B.P. 68 - 78340 Les Clayes-sous-Bois
* Description: This is this repo Jenkinsfile (the Jenkins pipeline recipe).
*              Its goal is to explicitely load the shared-libraries, then call
*              the global Jenkinsfile.
*/

// Load shared-libraries
String branchName = env.BRANCH_NAME
String tagName = params.UI_TAG

print("### Entering Jenkinsfile [branch: $branchName, tag=$tagName]")
if (tagName != 'none') {
    print('### Using tag...')
    new JenkinsUtils().loadSharedLibraries(this, tagName)
} else {
    print('### Using branch...')
    new JenkinsUtils().loadSharedLibraries(this, branchName)
}

// Call the global Jenkinsfile
print('### Calling global Jenkinsfile')
jenkinsfile('myqlm-simulators')
