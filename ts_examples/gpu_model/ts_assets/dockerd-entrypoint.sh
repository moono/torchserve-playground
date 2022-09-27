#!/bin/bash
set -e

if [[ "$1" = "serve" ]]; then
    shift 1
    torchserve --start \
    --ts-config /home/model-server/config.properties \
    --log-config /home/model-server/ts_log_config.xml
else
    eval "$@"
fi

# prevent docker exit
tail -f /dev/null