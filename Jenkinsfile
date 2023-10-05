/*
* Authors:     Atos BDS R&D CI/CD QLM Team
* Copyright:   2017-2023  Bull S.A.S. - All rights reserved.
*              This is not Free or Open Source software.
*              Please contact Bull SAS for details about its license.
*              Bull - Rue Jean Jaurès - B.P. 68 - 78340 Les Clayes-sous-Bois
* Description: This is this repo Jenkinsfile (the Jenkins pipeline recipe).
*              Its goal is to explicitely load our shared-libraries (priority
*              is given to the job's branch and if it does not exist for the
*              shared-library, then fallback to master).
*              Then call the global Jenkinsfile.
*/

print("### Entering Jenkinsfile [branch: $BRANCH_NAME]")

String repo, url, branch
Map sharedLibs = ['ci':       'ssh://git@qlmgit.usrnd.lan:22/brq/ci',
                  'qat':      'ssh://git@bitbucketbdsfr.fsc.atos-services.net:7999/brqext/qat',
                  'qlmtools': 'ssh://git@bitbucketbdsfr.fsc.atos-services.net:7999/brq/qlmtools'
                 ]
Object proc_name

for ( m in sharedLibs ) {
    StringBuilder out = new StringBuilder()     // Allocate new StringBuilder at each loop
    repo = m.key
    url = m.value
    branch = 'master'
    try {
        proc_name = "git ls-remote -h -- $url".execute()
        proc_name.consumeProcessOutput(out, out)
        print("> git ls-remote -h -- $url")
        proc_name.waitForOrKill(20000)
        if (out) {
            print(out)
            if (out.any { it.contains("$BRANCH_NAME") }) {
                branch = "$BRANCH_NAME"
            }
        } else {
            print('**** No output')
        }
    } catch (Exception e) {
        print("**** Fail to get available branches from $url\n$e\n")
    }
    library "$repo@$branch"
}

print('### Calling global Jenkinsfile')
jenkinsfile('myqlm-simulators')
