# Test description of scaling down apache
## Parameters in config
- period length: 30 seconds
- threshold: if cpu_user is under 30% 
- cooldown: one minute cooldown

## Initial setup
- 3 Webservers
- 1 loadbalancer

## Test 1: Phases
### Scale up apache (2x)
- Webserver
    - all > 30% cpu utilization for 31 seconds
- Load balancer: > 250ms response time for 31 seconds

### Expected Action
- Webserver instance should be created: webserver@8083
- Webserver instance should be created: webserver@8084

### Non-trigger
All webservers are running with > 30% cpu utilization for 31 seconds (trigger time) 
Loadbalancer is running with < 100ms response time for 31 seconds (trigger time)

#### Expected Action
- Nothing should happen

### Scale down apache
- Webserver 
    - instance 8080 is < 30% cpu utilization for 31 seconds (trigger time)
    - other instances > 30% cpu utilization for 31 seconds (trigger time)
- Load balancer: < 100ms response time for 31 seconds

#### Expected Action
Webserver instance 8080 should be removed

### Triggered while cooldown
- Webserver
    - instance 8081 with > 30% for 10 seconds (untrigger) then < 30% for 31 seconds (trigger time) then > 30% for 20 seconds
    - instance 8082 with < 30% for 61 seconds
- Loadbalancer: < 100ms response time for 31 seconds

#### Expected Action
Nothing should happen because everything happens during cooldown period

### Triggered during and after cooldown
- Webserver
    - instance 8081 with > 30% for 31 seconds (trigger time)
    - instance 8082 with < 30% for 31 seconds
- Loadbalancer: < 100ms response time for 31 seconds

#### Expected Action
Webserver instance 8082 should be removed because cooldown period is over and scale down rule is triggered
