#!/bin/bash
set -e

if [[ "$1" = "serve" ]]; then
    shift 1

    if [[ -z "$1" ]]; then
        torchserve --start \
        --ts-config /home/model-server/config.properties \
        --log-config /home/model-server/ts_log_config.xml
    else
        torchserve --start \
        --models "$1=$2" \
        --ts-config /home/model-server/config.properties \
        --log-config /home/model-server/ts_log_config.xml
    fi
else
    eval "$@"
fi

# prevent docker exit
tail -f /dev/null