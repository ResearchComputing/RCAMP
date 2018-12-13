#!/bin/bash

cp -f rcamp.dev.service /etc/systemd/system/rcamp.dev.service
cp -f rcamp.prod.service /etc/systemd/system/rcamp.prod.service
systemctl daemon-reload

systemctl enable rcamp.${1}
