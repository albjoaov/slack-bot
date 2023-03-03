#!/usr/bin/env bash
# exit on error
set -o errexit

# Install PDM and download dependencies
curl -sSL https://raw.githubusercontent.com/pdm-project/pdm/main/install-pdm.py | python3 -
export PATH=/opt/render/.local/bin:$PATH
pdm install --production --verbose

python app.py
