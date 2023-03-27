# torchserve-playground


## Q1. What happens if the requests overflows queue size?
* Torchserve will accepts `job_queue_size` requests concurrently,
  * `job_queue_size` can be specified in `config.perperties`
* At this moment, following requests will just return `healthy` response.
  * health check: `http://localhost:8080/ping`
  * describe model: `http://localhost:8081/models/empty_model`
* If the request exceeds current `job_queue_size` then following error will be returned,

```json
{
  'code': 503, 
  'type': 'ServiceUnavailableException', 
  'message': 'Model "empty_model" has no worker to serve inference request. Please use scale workers API to add workers.'
}
```
