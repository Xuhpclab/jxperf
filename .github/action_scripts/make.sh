#! /bin/bash

DIR=$(cd "$(dirname "$0")";pwd)

git submodule update --init --recursive
cd $DIR/../../thirdparty/watchpoint-lib && make install PREFIX=$DIR/../../build/thirdparty
cd $DIR/../../thirdparty/xed && ./mfile.py --debug --shared --prefix=$DIR/../../build/thirdparty install
cd $DIR/../../thirdparty/libpfm-4.10.1 &&  make PREFIX=$DIR/../../build/thirdparty install
cd $DIR/../../thirdparty/boost && sh ./bootstrap.sh --prefix=$DIR/../../build/thirdparty --with-libraries="filesystem"  cxxflags="-std=c++11" && ./b2 -j 4 && ./b2 filesystem install
cd $DIR/../../thirdparty/bintrees &&  python setup.py install --user