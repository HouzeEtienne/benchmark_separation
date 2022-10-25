# Benchmarking of Source Separation methods

*Author: Étienne Houzé, Preligens*

## Context
ROAC project for reasearch team.

Source separation has been identified as one of the many challenges one should overcome to acheive good identification and classification of submarine accoustic signals.

This repo contains code to test different existing approaches on the same tasks.

## How to use
The script can be used as a standalone, or with the docker image built from the Dockerfile.

To build the docker image, just run `./make.sh`.

Then, to run the container, use, for instance (other options may be used):
```bash
docker run  --rm -v [PATH TO DATA FOLDER]:/home/user/audioset -v $(PWD):/home/user audioset_tool python main.py [OPTIONS]
```
