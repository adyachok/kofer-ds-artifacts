def final projectId = 'zz'
def final componentId = 'ds-artifacts'
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
      image: "${dockerRegistry}/cd/jenkins-slave-python",
      workingDir: '/tmp',
      alwaysPullImage: true,
      args: '${computer.jnlpmac} ${computer.name}'
    ),
    containerTemplate(
      name: 'python-venv',
      image: "${dockerRegistry}/zz-cd/python-venv",
      alwaysPullImage: true,
      ttyEnabled: true,
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
}

def stageBuild(def context) {
    String deploymentNamespace = context.gitBranch == 'master' ? 'zz-test' : 'zz-dev'
    withEnv(["TAGVERSION=${context.tagversion}",
             "NEXUS_HOST=${context.nexusHost.replace('http://', '')}",
             "NEXUS_USERNAME=${context.nexusUsername}",
             "NEXUS_PASSWORD=${context.nexusPassword}",
             "GIT_BRANCH=${context.gitBranch}",
             "GIT_COMMIT=${context.gitCommit}",
             "DEPLOYMENT_NAMESPACE=${deploymentNamespace}"]) {

      stage('Build') {
             sh """
                oc get pods &&
                ls -la &&
                git checkout \$GIT_COMMIT
              """
              String changedFiles = sh (
                  script: 'git log -m -1 --name-only --pretty="format:" \$GIT_COMMIT',
                  returnStdout: true
              ).trim()

              String[] changedFilesList = changedFiles.split('\n')
              Set<String> modelPaths = []

              for (String path : changedFilesList) {                
                Boolean is_model_change = path.contains("build")
                if (is_model_change) {
                  // Adding changed model path to set
                  modelPaths.add(path.split("build")[0])
                }
              }
              // Start of model training loop
              for (String modelPath : modelPaths) { 
                 modelName = modelPath.split("/")[-1]              
                  withEnv(["MODEL_PATH=${modelPath}", "MODEL_NAME=${modelName}"]) {   
                    container('python-venv') {                 
                        println "Starting build process in path ${modelPath}"
                        stage('Test') {
                          def status = sh(
                            script: """
                              echo \$MODEL_PATH &&
                              cd \$MODEL_PATH &&
                              # pip install --user virtualenv &&
                              # virtualenv venv &&
                              #. venv/bin/activate &&
                              . /opt/venv/bin/activate &&
                              pip install -r requirements.txt &&
                              pip install -r test_requirements.txt &&
                              nosetests -v
                            """,
                            returnStatus: true
                          )
                        } // End of stage Test
                        stage('PEP-8') {
                          def status = sh(
                            script: """
                              cd \$MODEL_PATH &&
                              # . venv/bin/activate &&
                              . /opt/venv/bin/activate &&
                              pycodestyle --show-source --show-pep8 . &&
                              pycodestyle --statistics -qq  .
                            """,
                            returnStatus: true
                          )
                        } // End of stage PEP-8
                        stage('Build a model') {
                          String packageRootPath = MODEL_PATH.split("/").dropRight(2).join("/")
                          withEnv(["PACKAGE_ROOT_PATH=${packageRootPath}"]) {
                            def status = sh(
                              script: """
                                tree . &&
                                cd \$MODEL_PATH &&
                                tree . &&
                                . /opt/venv/bin/activate &&
                                export PYTHONPATH=\${PACKAGE_ROOT_PATH}/utils &&
                                python build/scripts/train_model.py &&
                                tree .
                              """,
                              returnStatus: true
                            )
                            if (status != 0) {
                              error "Model build failed!"
                            }
                          } // End withEnv
                        } // End of Build model
                        stage('Copy built model') {
                          def status = sh(
                            script: """
                              cd \$MODEL_PATH &&
                              mv model/* docker/ &&
                              tree .
                            """,
                            returnStatus: true
                          )
                          if (status != 0) {
                            error "Model copy failed!"
                          }
                        } // End copy build model                        
                    } // End of Container python-env

                    stage('Deploy built model') {
                        def status = sh(
                          script: """
                            cd \$MODEL_PATH &&
                            echo \$MODEL_PATH &&
                            echo \$MODEL_NAME &&
                            RESULT=`oc get bc \$MODEL_NAME --ignore-not-found=true --no-headers=true -n \$DEPLOYMENT_NAMESPACE` &&
                            if [ -n "\$RESULT" ]; 
                              then
                                echo "Run start-build"
                                pwd
                                oc start-build \$MODEL_NAME --from-dir=docker --follow -n \$DEPLOYMENT_NAMESPACE
                              else
                                echo "Run new-app"
                                pwd
                                oc new-build --name=\$MODEL_NAME --binary=true -n \$DEPLOYMENT_NAMESPACE &&
                                oc start-build \$MODEL_NAME --from-dir=docker --follow -n \$DEPLOYMENT_NAMESPACE &&
                                oc new-app \$MODEL_NAME -n \$DEPLOYMENT_NAMESPACE -e MODEL_NAME=\$MODEL_NAME
                            fi
                          """,
                          returnStatus: true
                        )
                        if (status != 0) {
                              error "Model deploy failed!"
                        }
                    } // End copy build model
                } // End of withEnv
              } // End of model training loop
              
            sh """
            # TODO: get model and put it within docker file
            # cp -r src docker/dist
            # TODO: check if component already exists (oc get bc)
            # TODO: trigger build
                ls -la
            """
      }
    }
}