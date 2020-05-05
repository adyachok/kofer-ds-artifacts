# Data Science Models and Algorithms

![alt text][logo]

[logo]: img/savedmodel%20with%20business.png "Logo"

### Description

*zz-ds-artifacts* is the repository to store data science models and other 
artifacts. The repository facilitates work of a data scientist intotuding logic 
for model building and deployment, which is a part of Jenkinsfile.


**DISCLAIMER** the service is the integral part of ZZ project, but because the 
project is build using **service choreography architecture pattern** there are 
no strong, tight relations in it. This means that every part of ZZ can be 
modified - removed - rewritten accordingly to the needs of customer.


### How it works

Every folder in **models** folder represent a data science model. Every folder 
should consist of next subfolders:
- **data** - this folder contains data using which model will be built
- **scripts** - this folder has to contain **train_model.py** script which should 
describe model. train and validate it.
- **docker** - contains docker file for serving a model.
- **model** - should contain **model.desc.yml** which will be later integrated as
a model's business metadata later. Also *train_model.py* should place own output
(a model) here


**IMPORTANT** every model folder name  should start from **mod-**


**Jenkinsfile** tracks changes in every model's data and scripts subdirectories.
If changes are found, for every model it  will start the build process.


The build process consists of the next steps:
- Install dependencies and run model tests and PEP8 tests.
- Create a second slave and compile, trane and validate a model there.
- Copy built model on the first slave and deploy it in the project. In case of 
a new model all OpenShift entities are created(build config, deployment config,
service...)
- Upload logs to the TensorFlow Dashboard.

The main post processing logic can be found in **utils/saver.py**

![alt text][schema]

[schema]: img/how%20ds-artifact%20works.png "Title"

#### TensorFlow Dashboard

TF Dashboard proposes reach UI interface for model training and validation. This
interface is flexible for customization.


Test instance can be found here: 
[Tensorboard](https://tensorboard-zz-cd.22ad.bi-x.openshiftapps.com/)

![alt text][dashboard]

[dashboard]: img/tensorboard.png "Tensorboard"

User can customize logs directly in his/her scripts.

### How to
- [Python tests assertions](https://www.tutorialspoint.com/unittest_framework/unittest_framework_assertion.htm)
- Install dependencies:
    ```bash
    # Before all  (only once):
  
    pip install -r test-requirements.txt
    ```
- Run tests:
    ```bash 
    # Run tests:
    
    nosetests tests/
    ```

### Convensions
- Every data-science model file name should start from **mod_**