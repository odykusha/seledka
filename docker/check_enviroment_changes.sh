#!/bin/sh

CHECK_FILES="
./docker/Dockerfile
./docker/entrypoint.sh
./docker/selenium.txt
./requirements.txt
"

cat ${CHECK_FILES} | shasum | cut -d ' ' -f 1
