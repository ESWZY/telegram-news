#!/bin/sh

# Set up the Heroku scheduler to run this command every hour. See example setup at https://goo.gl/nMCSH3
#
# Requires env vars to be set in Heroku with `heroku config:set`:
#  - HEROKU_APP_NAME:  this is just the app name in Heroku, i.e. `heroku apps` will list all apps you have access to
#  - HEROKU_CLI_USER:  Once Heroku CLI is authenticated (https://goo.gl/Qypr4x), check `cat .netrc` (or `_netrc` on Windows),
#                      look for `login` under `machine api.heroku.com`
#  - HEROKU_CLI_TOKEN: As above, but use the `password` field
#
# It helps if this file has execute privileges `chmod +x restart.sh`
#
# Test this script works by running `heroku run "~/restart.sh"`
#
# Heroku API: Restart all Dynos, see https://devcenter.heroku.com/articles/platform-api-reference#dyno-restart-all
curl -X DELETE "https://api.heroku.com/apps/${HEROKU_APP_NAME}/dynos" \
  --user "${HEROKU_CLI_USER}:${HEROKU_CLI_TOKEN}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/vnd.heroku+json; version=3"