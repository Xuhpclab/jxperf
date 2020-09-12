#! /bin/bash

DIR=$(cd "$(dirname "$0")";pwd)/../..

git submodule update --init --recursive
cd $(DIR)/thirdparty/watchpoint-lib && make install PREFIX=$(CURRENT_DIR)/build/thirdparty