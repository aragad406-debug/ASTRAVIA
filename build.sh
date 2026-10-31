#!/usr/bin/env bash
set -euo pipefail

pip install --upgrade pip

if [ "${MEDIA_STORAGE:-local}" = "s3" ]; then
  pip install -r requirements-s3.txt
else
  pip install -r requirements.txt
fi

python manage.py collectstatic --noinput --clear --verbosity 2

python -c "import json, pathlib; p=pathlib.Path('staticfiles/staticfiles.json'); assert p.is_file(), 'ERROR: staticfiles.json was not generated'; d=json.loads(p.read_text()); assert 'css/astravia.css' in d['paths'], 'ERROR: css/astravia.css is missing from manifest'; print('SUCCESS: ASTRAVIA CSS exists in staticfiles manifest')"
