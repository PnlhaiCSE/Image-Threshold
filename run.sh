#!/bin/bash

set -e

if ss -ltn | grep -q ':5000 '; then
    echo ""
    echo ">>>  Error: Port 5000 đang dùng rồi :()  <<<"
    exit 1
fi

docker compose up -d --build
echo ">>> run thành công <<<"