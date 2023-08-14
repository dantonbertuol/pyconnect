#!/usr/bin/env bash
PATH_UTILS=$HOME/.local/bin/pyconnect_utils
PATH_BIN=$HOME/.local/bin
PATH_DESKTOP=$HOME/.local/share/applications
PATH_ICON=$HOME/.icons
mkdir -p $PATH_UTILS
mkdir -p $PATH_BIN
mkdir -p $PATH_DESKTOP
mkdir -p $PATH_ICON
cp pyconnect_utils/pyconnect-dark.qss $PATH_UTILS
cp pyconnect_utils/pyconnect-icon.png $PATH_UTILS
cp pyconnect_bin/pyconnect $PATH_BIN
cp pyconnect_utils/pyconnect.desktop $PATH_DESKTOP
cp pyconnect_utils/pyconnect-icon.png $PATH_ICON