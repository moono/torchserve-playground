# torchserve-playground


## Q1. What happens if the requests overflows queue size?
* Torchserve will accepts `job_queue_size` requests concurrently,
  * `job_queue_size` can be specified in `config.perperties`
* At this moment, following requests will just return `healthy` response.
  * health check: `http://localhost:8080/ping`
  * describe model: `http://localhost:8081/models/empty_model`
* If the request exceeds current `job_queue_size` then following error will be returned,

```yaml
{
    'code': 503, 
    'type': 'ServiceUnavailableException', 
    'message': 'Model "empty_model" has no worker to serve inference request. Please use scale workers API to add workers.'
}
```

## Q2. How to check model status (Not using `/ping` endpoint)
* Inference API(8080)'s `/ping` endpoint is used for frontend (java server)
* use Management API(8081)'s model describe endpoint `/models/<model-name>`
* will return something like
```yaml
# Model ready / healthy ==> handler's initialize() method completed
[
    {
        "modelName": "empty_model",
        "modelVersion": "1.0",
        "modelUrl": "empty_model.mar",
        "runtime": "python",
        "minWorkers": 1,
        "maxWorkers": 1,
        "batchSize": 1,
        "maxBatchDelay": 100,
        "loadedAtStartup": true,
        "workers": [
            {
                "id": "9000",
                "startTime": "2023-04-18T00:28:02.086Z",
                "status": "READY",
                "memoryUsage": 0,
                "pid": 70,
                "gpu": false,
                "gpuUsage": "N/A"
            }
        ]
    }
]

# Model not ready / unhealthy ==> handler's initialize() method failed
[
    {
        "modelName": "empty_model",
        "modelVersion": "1.0",
        "modelUrl": "empty_model.mar",
        "runtime": "python",
        "minWorkers": 1,
        "maxWorkers": 1,
        "batchSize": 1,
        "maxBatchDelay": 100,
        "loadedAtStartup": true,
        "workers": [
            {
                "id": "9000",
                "startTime": "2023-04-18T00:28:02.086Z",
                "status": "UNLOADING",
                "memoryUsage": 0,
                "pid": 70,
                "gpu": false,
                "gpuUsage": "N/A"
            }
        ]
    }
]
```