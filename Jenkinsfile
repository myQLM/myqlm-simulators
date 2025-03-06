/*
* Authors:     Atos BDS R&D CI/CD Qaptiva Team
* Description: This is this repo Jenkinsfile (the Jenkins pipeline recipe).
*              Its goal is to explicitely load the shared-libraries, then call
*              the global Jenkinsfile.
*/

// Load shared-libraries
print("### Entering Jenkinsfile [branch: $BRANCH_NAME]")
new JenkinsUtils().loadSharedLibraries(this, BRANCH_NAME)

// Call the global Jenkinsfile
print('### Calling global Jenkinsfile')
jenkinsfile('myqlm-simulators')
