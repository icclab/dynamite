# Test description of scaling up apache
## Parameters in config
- period length: 30 seconds
- threshold: if response time of loadbalancer is above 250ms 
- cooldown: one minute cooldown

## Initial setup
- 2 Webservers
- 1 loadbalancer

## Phases
All webservers are running with > 30% cpu utilization for the whole test (avoid scale down)

### Non-trigger
Loadbalancer is running with < 100ms response time for 60 seconds

#### Expected Action
- Nothing should happen

### Scale up apache
- Load balancer: > 250ms response time for 31 seconds

### Expected Action
- Webserver instance should be created: webserver@8082

### Triggered while cooldown
- Loadbalancer: > 250ms response time for 50 seconds

#### Expected Action
Nothing should happen because everything happens during cooldown period

### Triggered during and after cooldown
- Loadbalancer: < 250ms response time for 20 seconds then > 250ms for 31 seconds 

#### Expected Action
Webserver instance 8083 should be created because cooldown period is over and scale up rule is triggered

## Expected Result after test
Running instances:
- webserver@8080
- webserver@8081
- webserver@8082
- webserver@8083