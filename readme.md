# Dynamite: Scaling Engine for CoreOS
Disclaimer: This application currently is in its incubating state and under heavy deplyoment

Dynamite's ultimate goal is to manage the deployment and the automatic scaling of a dockerized application on CoreOS.

Dynamite heavily levarages fleet to achieve this
  * It assumes that *fleet* was used to describe the composition of an application
  * It assumes that those fleet service files start/stop docker containers 

 
## General Idea / How to use
### Requirements
1. You need to have a dockerized application
2. You need the necessary fleet files to manage those containers
 1. Specifiying how containers should be deployed on a CoreOS Cluster

### Using Dynamite
1. Create a configuration file for your application. A pretty self-explaining example can be found [here](https://github.com/sandorkan/dynamite/blob/master/dynamite/tests/TEST_CONFIG_FOLDER/config.yaml)
 1. State where fleet files lie (default: /etc/dynamite/service-files)
 2. State Fleet API Endpoint
 3. State services used by the application
 4. Define scaling policies
 
 ## Technical Documentation
 
### etcd paths
Dynamite uses etcd to write the state of the application its configuration and the fleet unit files of all services to.   
Everything written to etcd from dynamite is saved in the hidden folder `/_dynamite`.

#### /_dynamite/state/application_status
This is the status of dynamite. It allows dynamite to recover from failure.

#### /_dynamite/run/service
This  folder contains a subfolder for each service running. 
Inside the folder there is a fleet service template key (`/_dynamite/run/service/<service_name>/fleet_service_template`) where the description of the service (as JSON) is written to.
The description (JSON) of all the created instances of the service are also available in this folder (`/_dynamite/run/service/<service_name>/<instance_name>`)

#### /_dynamite/init/application_configuration
The dynamite configuration file (YAML) is read at startup, transformed to JSON and written to etcd in the path `/_dynamite/init/application_configuration`.