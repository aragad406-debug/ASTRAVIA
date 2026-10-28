#!/usr/bin/env bash
# Render build command. Exits on the first error so a broken build never deploys.
set -o errexit
set -o pipefail

pip install --upgrade pip
if [ "${MEDIA_STORAGE:-local}" = "s3" ]; then
  pip install -r requirements-s3.txt
else
  pip install -r requirements.txt
fi

python manage.py collectstatic --noinput
# Migrations run on Render's pre-deploy step (see render.yaml) so a failed migration stops the release.
