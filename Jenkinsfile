/*
* Authors:     Atos BDS R&D CI/CD Qaptiva Team
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
