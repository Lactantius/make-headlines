#!/usr/bin/env bash

set -e
#flask db upgrade
gunicorn -c gunicorn.config.py wsgi:app
