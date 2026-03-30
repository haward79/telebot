#!/bin/bash

cd "$(dirname "$(realpath "$0")")" || {
    echo 'FATAL: Failed to change working dir to project root'
    exit 1
}

[[ -z "$1" ]] && {
    echo 'FATAL: please specify python script name to run'
    exit 2
}

py_script="${1}.py"

[[ -f "$py_script" ]] || {
    echo "FATAL: the python script $py_script is NOT a regular file"
    exit 3
}

docker compose exec app python "$py_script" "${@:2}"
