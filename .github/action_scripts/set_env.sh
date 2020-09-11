export JXPerf_HOME=${{ github.workspace }}
export LD_LIBRARY_PATH=$JXPerf_HOME/bin/kissmalloc:$JXPerf_HOME/build/preload:$LD_LIBRARY_PATH
export JAVA_AGENT=$JXPerf_HOME/thirdparty/allocation-instrumenter/target/java-allocation-instrumenter-HEAD-SNAPSHOT.jar
