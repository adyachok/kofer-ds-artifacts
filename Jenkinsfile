def final projectId = 'smart'
def final componentId = 'data-science-artifacts'
def final credentialsId = "${projectId}-cd-cd-user-with-password"
def sharedLibraryRepository
def dockerRegistry
node {
  sharedLibraryRepository = env.SHARED_LIBRARY_REPOSITORY
  dockerRegistry = env.DOCKER_REGISTRY
}

library identifier: 'ods-library@production', retriever: modernSCM(
  [$class: 'GitSCMSource',
   remote: sharedLibraryRepository,
   credentialsId: credentialsId])

// See readme of shared library for usage and customization.
odsPipeline(
  podContainers: [
    containerTemplate(
      name: 'jnlp',
      image: "${dockerRegistry}/cd/jenkins-crafty-slave-python",
      workingDir: '/tmp',
      alwaysPullImage: true,
      resourceRequestMemory: '1Gi',
      resourceLimitMemory: '2Gi',
      args: '${computer.jnlpmac} ${computer.name}'
    ),
    containerTemplate(
      name: 'python',
      image: 'python:3.8-slim',
      alwaysPullImage: true,
      ttyEnabled: true,
      resourceRequestMemory: '1Gi',
      resourceLimitMemory: '2Gi',
      command: '',
      workingDir: '/tmp'
    )
  ],
  projectId: projectId,
  componentId: componentId,
  openshiftBuildTimeout: 25,
  branchToEnvironmentMapping: [
    'master': 'test',
    '*': 'dev'
  ]
) { context ->
  stageBuild(context)
  stageScanForSonarqube(context)
}

def stageBuild(def context) {
    withEnv(["TAGVERSION=${context.tagversion}",
             "NEXUS_HOST=${context.nexusHost.replace('http://', '')}",
             "NEXUS_USERNAME=${context.nexusUsername}",
             "NEXUS_PASSWORD=${context.nexusPassword}",
             "GIT_BRANCH=${context.gitBranch}",
             "GIT_COMMIT=${context.gitCommit}"]) {

      stage('Build') {
             sh 'oc get pods'
             sh """
                mkdir docker/dist
                cp -r src docker/dist
              """
              container('python') {
                stage('Build a Go project') {
                    sh """
                        python --version &&
                        pip install numpy pandas matplotlib
                    """
                }
            }
      }

    }
}