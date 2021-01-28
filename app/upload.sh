#!/bin/bash

if [[ "$UPLOAD_SERVER" == "" ]]; then
    echo "Missing UPLOAD_SERVER";
    exit 1;
fi

curl -T /var/plandata/out/data.json ftp://${UPLOAD_SERVER} --user ${UPLOAD_USER}:${UPLOAD_PASS}