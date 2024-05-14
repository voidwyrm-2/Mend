#!/bin/sh

# script to help me commit changes faster

if [ $# -ne 1 ]; then
    printf "zsh|bsh|sh commit.sh [version]"
    exit 1
fi

if [ "$1" = "-h" ]; then
    printf "zsh|bsh|sh commit.sh [version]"
    exit 1
fi

#if [ "$1" = "-v" ]; then
#    printf "previous version was: "
#    exit 1
#fi

git add .

git commit . -m "language version is now $1, see readme for details"