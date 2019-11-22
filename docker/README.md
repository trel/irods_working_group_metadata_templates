# Docker environment for testing JSON<>AVU and related work

## Introduction

This is a docker environment to test the [irods_avu_json](https://github.com/MaastrichtUniversity/irods_avu_json) Python 
module. Please read the README of that repository for an introduction into the goals of this work.

The repository [irods_avu_json-ruleset](https://github.com/MaastrichtUniversity/irods_avu_json) contains the iRODS rules, policies and microservices to make the conversion code operational in iRODS.

This docker-compose binds everything together in a docker example.

## Running
This will spawn the iRODS catalog provider container and a postgres DB container.
```
docker-compose build
docker-compose up
```

## Testing
A small test script is available in `/irods_avu_json-ruleset/tests/pep_tests.sh`. This script throws lots of errors
and warnings, but should report when a unexpected error happens.

You can run it using
```
docker exec -it irods_avu_json-docker_irods-provider_1 bash
su - irods
cd /irods_avu_json-ruleset/tests
bash pep_tests.sh
```

## Authors
Paul van Schayck (p.vanschayck@maastrichtuniversity.nl), Ton Smeele, Daniel Theunissen and Lazlo Westerhof 

