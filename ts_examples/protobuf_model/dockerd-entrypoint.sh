#!/bin/bash
set -e

if [[ "$1" = "serve" ]]; then
    shift 1

    if [[ -z "$1" ]]; then
        torchserve --start --ts-config /home/model-server/config.properties
    else
        torchserve --start --models "$1=$2" --ts-config /home/model-server/config.properties 
    fi
else
    eval "$@"
fi

# prevent docker exit
tail -f /dev/null