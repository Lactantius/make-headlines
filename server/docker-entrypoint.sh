#!/usr/bin/env bash

set -e
#flask db upgrade
gunicorn app:app --timout 45
