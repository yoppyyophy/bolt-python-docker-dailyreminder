#!/bin/bash
cd `dirname $0`

export PORT=8080

docker build --force-rm=true --no-cache=true -t dailyreminder_test ../

docker run -dit \
  --name dailyreminder_test \
  -p 8080:$PORT \
  -e SLACK_SIGNING_SECRET=$SLACK_SIGNING_SECRET \
  -e SLACK_BOT_TOKEN=$SLACK_BOT_TOKEN \
  -e GOOGLE_APPLICATION_CREDENTIALS=$GOOGLE_APPLICATION_CREDENTIALS \
  -e PORT=$PORT \
  dailyreminder_test
