#!/bin/sh

CHECK_FILES="
./docker/Dockerfile
./docker/selenium_env.txt
./docker/requirements.txt
"

cat ${CHECK_FILES} | shasum | cut -d ' ' -f 1
