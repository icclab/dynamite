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

## Concepts
There are a few things you should now about dynamite before using it. The following sections provide some basic information about how dynamite works and what features it has.

### Services
Dynamite assumes that your application can be split in many different services. If this is not the case, dynamite isn't that useful because the smallest unit dynamite can handle is a service. Usually you want a scaling engine to scale up or scale down the application and dynamite achieves that by creating new resp. destroying existing services. That's why the application should consist of services, otherwise it won't be scalable at all (at least not by dynamite).  
When we talk about services in this document we mean fleet services.

### Etcd for service registry & metrics storage
Dynamite depends on etcd and fleet. If none of them are running in your environment, dynamite is probably not the right tool for you. It is also important that the services of the application behave in a way that dynamite is able to get some information about them from etcd.

Dynamite requires that each service instance registers itself to etcd. The path is built dynamically from the information given through the configuration file. Dynamite needs to resolve a service id to a service instance name.   
This is why it searches the key `service_instance_name` in the etcd path: `$application_base_path/$service_type/$service_instance_uuid/`.
A service should register like that in etcd:
```
$application_base_path/$service_type/$service_instance_uuid/service_instance_name

# Concrete example: 
/services/webserver/9ed076d2-f6f0-42c0-ae04-63c817abe456/service_instance_name
```

But also the metrics need to be in a defined path (dynamically generated):
```
$metrics_base_path/$service_type/$service_instance_uuid/$metric/$date

# Concrete example:
/metrics/webserver/88e9916e-2342-4acf-a93a-1e3a6551c1da/cpu_user/2015-07-28T13:15:50.631Z
```
The value of the metric key is either in JSON format or just a single value.

Explanation of the dynamic path contents:
  * $metrics_base_path and $application_base_path can be defined by the user in the configuration file
  * $service_type: The service type is read from the configuration file (scaling policy)
  * $service_instance_uuid: An ID for the service instance. You can use your own IDs to identify service instances. It does not matter how you generate this ID. (UUID recommended)
  * $metric: the metric name defined in the scaling policy in the configuration file.
  * $date: The date the metric was collected (ISO 8601 with 3 positions after the decimal point)

### Scaling Policies
Dynamite makes scaling decisions based on rules written in the configuration file. There are some features that avoid several problems when you do scaling:  
In the configuration you define a scaling policy that can be referenced by a service as scale up or scale down policy. Basically you only specify what metric is of interest and what type of service is it from. Then you define a threshold.
If the metric falls below (or exceeds) the threshold the policy is triggered. But instead of executing a scaling action a timer is started. If this timer is up and all incoming metric values are under resp. over the threshold then the scaling action is executed. If a metric value is read that doesn't fall below resp. exceeds the threshold then the timer is reset. This timer (attribute *period* in the configuration) avoids that single events can cause a lot of scaling actions.

Another problem is that a scaling action can be executed right after it was already executed. It could occur that a service is under heavy load and a scaling action is executed (e.g. a webserver is spawned to handle more traffic). Before the service is really running or the effect of the additional service is visible the next scaling action is already executed. To avoid this scenario a cooldown period can be defined per scaling policy. That means that if a scaling action would be executed and is within the cooldown period (started when the last scaling action was issued) the scaling action is not taking place.

### Port mapping
An important thing to mention is how networking works with fleet on CoreOS. Unless you use something like [flannel](https://github.com/coreos/flannel) (virtual network) use need to use port mapping to expose ports from the docker containers to the host. This seems straight forward but is a bit cumbersome and dangerous in the case that nobody prevents you from starting two services that use the same ports. The only thing you'll notice is failed services.  
To avoid this problem there is a simple trick: Set the instance name of a fleet service to the port number it uses. This way the service knows to what port to map to (access the service name with %i) and it is not possible to submit two services with the same port number of the same unit file to fleet. If a service uses multiple ports they have to be mapped sequentially by incrementing the base port number.  

Example:
```
container: loadbalancer with port 80 as frontend port and 1936 as admin page port  
  1. choose base port number: e.g. port 8080 (configuration file of dynamite, attribute: base_instance_prefix_number)
  2. set number of ports: set to 2 (configuration file of dynamite, attribute: ports_per_instance)
  3. The service has to map port 80 to port 8080 and port 1936 to 8081 (this needs to be done in the fleet unit file)
```

### Resilience
Dynamite is designed to be resilient if run in a container. That means that dynamite saves its state into etcd and if it crashes it can continue when restarted. All you need to do is to run dynamite in a container that was started by a fleet service. Set the `Restart` property of the fleet service so that the container is restarted on failure. This way the scaling engine can continue working even if the host that runs the dynamite container crashes because it will be restarted on another node in the cluster.

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
The type of the service to read the metrics from. 

#### Metric
The name of the metric the policy depends on. Dynamite will read these metrics from etcd and compare them with the threshold specified.

#### Metric aggregated
Defines if the metric is aggregated over all instances of the service (aggregated is true) or if each service instance writes its own metrics (aggregated is false).

#### Comparative operator
This operator defines how the comparision with the threshold should be made. The comparision statement is: 'actual value' (lt|gt) 'threshold value' where lt or gt are comparative operators for < and >.

#### Threshold
The threshold value when the rule should be triggered.

#### Threshold unit
The unit of the threshold value. No unit conversion is made. It exists just for description purposes and clarity for the reader.

#### Period
The amount of time the scaling policy should be triggered before generating a scaling action.

#### Period unit
The unit of the period time. This unit has effect how the number of the attribute *period* is handled. Valid units are:
  * second
  * minute
  * hour

#### Cooldown period
The amount of time the scaling policy is in standby after triggering.

#### Cooldown period unit
The unit of the cooldown period time. This unit has effect how the number of the attribute *cooldown period* is handled. Valid units are:
  * second
  * minute
  * hour

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

## Install dynamite (Ubuntu 14.04)
The instructions below describe how to install dynamite on a ubuntu system. However consider using the [docker image](https://registry.hub.docker.com/u/icclabcna/zurmo_dynamite/).
```
# install required packages
apt-get update && apt-get install -yq python3 \
	git \
	curl \
	python3-setuptools \
	python3-pip \
	libssl-dev \
	libffi-dev

# clone the repository
git clone https://github.com/icclab/dynamite.git
cd dynamite
./setup.py install
cd dist
easy_install dynamite*.egg
mkdir /etc/dynamite
mkdir /var/log/dynamite
```

## Start dynamite
The following command starts dynamite with all its arguments:
```
/usr/local/bin/dynamite 
    --config_file /path/to/config.yaml 
    --service_folder /path/to/fleet-services 
    --etcd_endpoint 127.0.0.1:4001
    --fleet_endpoint 127.0.0.1:49153
```
  Arguments:
   * __config_file:__ Path to the dynamite (yaml) config file (default: /etc/dynamite/config.yaml)
   * __service_folder:__ Path to the location of the service files (default: /etc/dynamite/service-files)
   * __etcd_endpoint:__ etcd API endpoint (default: 127.0.0.1:4001)
   * __fleet_endpoint:__ fleet API endpoint (default: 127.0.0.1:49153)
 
## Implementation Details
### Overview
![Dynamite in its components](https://raw.githubusercontent.com/icclab/dynamite/master/doc/DynamiteArchitecture.png)

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