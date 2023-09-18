#!/bin/bash
cd `dirname $0`

export PORT=8080

docker build --force-rm=true --no-cache=true -t dailyreminder_test ../

docker run -dit \
  --name dailyreminder_test \
  -p 8080:$PORT \
  -e GOOGLE_APPLICATION_CREDENTIALS=$GOOGLE_APPLICATION_CREDENTIALS \
  -e PORT=$PORT \
  dailyreminder_test
