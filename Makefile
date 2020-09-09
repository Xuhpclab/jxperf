.PHONY: thirdparty clean

CURRENT_DIR=$(shell pwd)

thirdparty:
	git submodule update --init --recursive
	cd thirdparty/watchpoint-lib && make install PREFIX=$(CURRENT_DIR)/build/thirdparty
	cd thirdparty/xed && ./mfile.py --debug --shared --prefix=$(CURRENT_DIR)/build/thirdparty install
	cd thirdparty/libpfm-4.10.1 &&  make PREFIX=$(CURRENT_DIR)/build/thirdparty install
	cd thirdparty/boost && sh ./bootstrap.sh --prefix=$(CURRENT_DIR)/build/thirdparty --with-libraries="filesystem"  cxxflags="-std=c++11" && ./b2 -j 4 && ./b2 filesystem install 
	cd thirdparty/bintrees &&  python setup.py install --user
	cd thirdparty/allocation-instrumenter && mvn package -DskipTests
	mkdir $(CURRENT_DIR)/build/preload
	cd preload && make
	cd src && make

clean:
	make -C src clean
	make -C preload clean
	make -C thirdparty/libpfm-4.10.1 clean
	cd thirdparty/xed && ./mfile.py clean
	make -C thirdparty/watchpoint-lib clean
	rm -rf build
	mvn -f thirdparty/allocation-instrumenter/pom.xml clean
