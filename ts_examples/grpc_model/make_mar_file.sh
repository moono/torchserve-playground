#!/bin/sh

# remove python cache file
echo "remove python cache file"
find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf

# move to current folder
cd ./ts_examples/grpc_model

# create *.mar files
torch-model-archiver --model-name grpc_model \
--version 1.0 \
--handler my_handler.py \
--extra-files grpc_model_pb2.py \
--export-path exported \
--force
