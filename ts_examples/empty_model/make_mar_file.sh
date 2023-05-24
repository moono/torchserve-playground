#!/bin/sh

# remove python cache file
echo "remove python cache file"
find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf

# move to current folder
cd ./ts_examples/empty_model

# create *.mar files
torch-model-archiver --model-name empty_model \
--version 1.0 \
--handler my_handler.py \
--extra-files log_config.py,my_models.py \
--config-file model-config.yaml \
--export-path exported \
--force
