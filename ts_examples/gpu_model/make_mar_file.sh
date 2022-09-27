#!/bin/sh

# remove python cache file
echo "remove python cache file"
find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf

# # make zip file
# mkdir -p ./extra-files
# zip -r ./extra-files/gpu_model.zip folder1/ folder2/ some_file.py

# create *.mar files
torch-model-archiver --model-name gpu_model \
--version 1.0 \
--handler my_handler.py \
--extra-files log_config.py \
--export-path ts_assets \
--force
