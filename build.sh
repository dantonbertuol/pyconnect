#!/usr/bin/env bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
pyinstaller -F --icon pyconnect_utils/pyconnect-icon.png pyconnect.py
mv dist/pyconnect pyconnect_bin
rm -rf build dist pyconnect.spec