#!/bin/bash

if [[ "$UPLOAD_SERVER" == "" ]]; then
    echo "Missing UPLOAD_SERVER";
    exit 1;
fi

cp /var/plandata/out/data.json data.json
#curl -v -ssl ftp://${UPLOAD_SERVER} -Q "DELE data.json" --user ${UPLOAD_USER}:${UPLOAD_PASS}
curl -T data.json --ssl ftp://${UPLOAD_SERVER} --user ${UPLOAD_USER}:${UPLOAD_PASS}