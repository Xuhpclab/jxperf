#! /bin/bash

DIR=$(cd "$(dirname "$0")";pwd)

git submodule update --init --recursive
cd $DIR/../../thirdparty/watchpoint-lib