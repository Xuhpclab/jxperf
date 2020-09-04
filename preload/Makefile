BUILD_DIR=$(shell pwd)/../build
export BUILD_DIR

CXX = g++
INC_DIRS = ../src/util

all: $(BUILD_DIR)/preload/libpreload.so
$(BUILD_DIR)/preload/libpreload.so: preload.cpp
	$(CXX) -I$(INC_DIRS) -std=c++11 -fPIC -shared preload.cpp -o $@ 

.PHONY: clean
clean :
	rm -rf $(BUILD_DIR)/preload/libpreload.so