#!/bin/sh



docker build . -t audioset_tool \
    --build-arg USER_ID=$(id -u) \
    --build-arg GROUP_ID=$(id -g)