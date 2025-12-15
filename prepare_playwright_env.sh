#!/bin/sh

set -e
# Install Python dependencies from requirements.txt
pip install -r requirements.txt

# Install Playwright browsers and OS dependencies
playwright install --with-deps chromium