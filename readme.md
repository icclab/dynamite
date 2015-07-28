# Dynamite: Scaling Engine for CoreOS
Dynamite's ultimate goal is to manage the deployment and the automatic scaling of a dockerized application on CoreOS.  

Dynamite heavily levarages fleet and etcd to achieve this
  * It assumes that *fleet* was used to describe the composition of an application
  * It assumes that those fleet service files start/stop docker containers
  * It assumes that the services are registered in *etcd*
  * It assumes that metrics are written to *etcd*

*Disclaimer: This application currently is in its incubating state and under heavy deplyoment*

## Requirements
1. You need to have a dockerized application
2. You need the necessary fleet files to manage those containers
3. The services need to register themselves to etcd
4. You need to have something that writes metrics to etcd (e.g. [logstash](https://www.elastic.co/products/logstash) with the [etcd output plugin](https://github.com/icc-bloe/logstash-output-etcd))
5. You need a cluster with fleet and etcd running on its nodes (e.g. [CoreOS](https://coreos.com/))

## Using Dynamite
Dynamite is designed to be used in a CoreOS cluster in a container. You should usually not need to install and run the application directly. Instead it is recommended that you use the existing [docker image](https://registry.hub.docker.com/u/icclabcna/zurmo_dynamite/) for dynamite. This way you only need to follow the instructions of how to use the docker image and write a configuration file for dynamite. 

## Configuration
Create a configuration file for your application. A pretty self-explaining example can be found [here](https://github.com/icclab/dynamite/blob/master/dynamite/tests/TEST_CONFIG_FOLDER/config.yaml).  
The configuration file (in [yaml](http://yaml.org/) format) consists of several sections:
 1. State where fleet files lie (default: /etc/dynamite/service-files)
 2. (Optional) State Fleet API Endpoint (you can tell this dynamite when starting by argument)
 3. Tell dynamite which etcd paths should be used for the metrics and for the service information
 4. State services used by the application
 5. Define scaling policies

### Fleet File Location
You need to tell dynamite which fleet files should be used for the services. The location has to be the folder your fleet files reside in. Actually you can define multiple folders as location.

#### Format
```
  ServiceFiles:
    PathList:
      <list of paths as strings>
```
#### Example
```
  ServiceFiles:
    PathList:
      - '/etc/dynamite/service-files'
      - '/tmp/dynamite/service-files'
```
### Fleet API Endpoint
Dynamite needs to know where fleet is running so it can start and stop fleet services. This value is optional and can also be specified as start argument for dynamite.

#### Format
```
  FleetAPIEndpoint:
    ip: <string>
    port: <int>
```
#### Example
```
  FleetAPIEndpoint:
    ip: 127.0.0.1
    port: 49153
```
### Etcd Paths
Define the base paths to the etcd paths where
  * your services are registered
  * the metrics of the services are written

#### Format
```
  ETCD:
    application_base_path: <string>
    metrics_base_path: <string>
```
#### Example
```
  ETCD:
    application_base_path: /services
    metrics_base_path: /metrics
```
### Service Description
This is the most important section in the configuration file. Here you need to define which services should be started, how many instances should be running at min/max and many other things. The details of the attributes are explained in detail in the next few sections:

#### name_of_unit_file
This is the name of the service. It should match the name of the fleet unit file except the suffix '.service'.

#### type
This specifies the type of the service. At the moment only one type is treated specially by dynamite. If you define an attached service you need to set the type to 'attached_service'. For other services it is recommended to define types like 'database' for databases, 'volume' for docker volumes but it does not affect the behaviour yet.

#### min_instance
Define the minimum of running services. If scale down policies are configured for this service this will ensure that at least the defined amount of services are running. So if a scale down policy is triggered the service will not be scaled down unless there are more than the minimum services running.   
At startup dynamite will start as many service instances as specified here.

#### max_instance
Define the maximum of running services. If scale up policies are configured for this service this will ensure that at most the defined amount of services are running. If a scale up policy is triggered the service will not be scaled up unless there are less than the maximum services running.

#### base_instance_prefix_number
Each instance of the service will be created with an instance name. When using dynamite this instance name is the port number used by the service. If the service uses more than one port, the instance name is the lowest port number of the service and you need to define the *ports_per_instance* attribute.  
For each created instance, the instance number will be increased by one (or by *ports_per_instance* if defined and >1)

#### ports_per_instance
This option specifies how many ports the service uses.

#### attached_service
You can define attached services that are part of the service. If a service instance is created or deleted, also the attached services will be created/deleted. The attached services' instance name will be the same as the instance name of the service.  
Attached services also need to be defined as service with the type set to 'attached_service'

#### scale_up_policy
Define a scale up policy for the service. Write the name of the scaling policy you want to use to scale up the service here. The scaling policy needs to be defined in the last section of the configuration file.

#### scale_down_policy
Define a scale down policy for the service. Write the name of the scaling policy you want to use to scale down the service here. The scaling policy needs to be defined in the last section of the configuration file.

#### Format
```
  Service:
    <service name as string>:
      name_of_unit_file: <service name as string>@.service
      type: <type of service as string>
      min_instance: <minimum service count as int>
      max_instance: <maximum service count as int>
      base_instance_prefix_number: <instance number (base port number) as int>
      ports_per_instance: <number of ports used by the service as int>
      attached_service:
        <name of attached services as list of strings>
      scale_up_policy:
        ScalingPolicy: <name of scaling policy as string>
      scale_down_policy:
        ScalingPolicy:  <name of scaling policy as string>
```
#### Example
```
  Service:
    apache:
      name_of_unit_file: apache@.service
      type: webserver
      min_instance: 2
      max_instance: 5
      base_instance_prefix_number: 8080
      ports_per_instance: 1
      attached_service:
        - apache_discovery
        - apache_logging
      scale_up_policy:
        ScalingPolicy: apache_scale_up
      scale_down_policy:
        ScalingPolicy: apache_scale_down
```
### Scaling Policy Description

#### Service type
#### Metric
#### Metric aggregated
#### Comparative operator
#### Threshold
#### Threshold unit
#### Period
#### Period unit
#### Cooldown period
#### Cooldown period unit


#### Format
```
  ScalingPolicy:
    <name of the scaling policy as string>:
      service_type: <type of the service to read the metrics from as string>
      metric: <name of the metric as string>
      metric_aggregated: <is the metric aggregated over all service instances as true or false>
      comparative_operator: <operator to compare the actual metrics with the threshold as lt or gt>
      threshold: <threshold to trigger the policy as int>
      threshold_unit: <threshold unit as string>
      period: <period in which the metric has to be over/under the threshold as int>
      period_unit: <unit of the period as second or minute or hour>
      cooldown_period: <cool down period as int>
      cooldown_period_unit: <unit of the cooldown period as second or minute or hour>
```
#### Example
```
  ScalingPolicy:
    apache_scale_down:
      service_type: webserver
      metric: cpu_user
      metric_aggregated: false
      comparative_operator: lt
      threshold: 7
      threshold_unit: percent
      period: 30
      period_unit: second
      cooldown_period: 1
      cooldown_period_unit: minute
```

 
## Implementation Details
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
