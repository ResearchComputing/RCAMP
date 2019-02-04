#!/bin/bash
docker exec rcamp-uwsgi bash -c "yum -y install openssl && useradd -M -p $(echo password | openssl passwd -1 -stdin) testuser1"
docker exec rcamp-uwsgi bash -c "useradd -M -p $(echo password | openssl passwd -1 -stdin) testuser2"
