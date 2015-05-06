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