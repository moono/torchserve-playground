# Torchserve gRPC test

## Prerequsite
* install dependencies
```bash
~$ pip install grpcio protobuf grpcio-tools googleapis-common-protos
```

## Note
* Take a look at official Torchserve proto files
* ref: https://pytorch.org/serve/grpc_api.html
* `inference.proto`
    * ❗input can only be `map<string, bytes>`
```proto
...
message PredictionsRequest {
    // Name of model.
    string model_name = 1; //required

    // Version of model to run prediction on.
    string model_version = 2; //optional

    // Input data for model prediction
    map<string, bytes> input = 3; //required

    // SequenceId is required for StreamPredictions2 API.
    optional string sequence_id = 4; //optional
}
...
```

## Model Preparation
* make `grpc_model.mar` file
```bash
# from project root
~$ bash ./ts_examples/grpc_model/make_mar_file.sh
```

## Test code Preparation
* generate protobuf for input / output serialization
```bash
~$ python -m grpc_tools.protoc \
-I ./test_scripts \
--proto_path=./test_scripts \
--python_out=./test_scripts \
./test_scripts/grpc_model.proto
```
