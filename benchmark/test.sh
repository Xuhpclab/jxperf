#! /bin/bash

# data-centric mode
# LD_PRELOAD=${CUR_DIR}/build/preload/libpreload.so
# java \
#     -javaagent:${CUR_DIR}/thirdparty/allocation-instrumenter/target/java-allocation-instrumenter-HEAD-SNAPSHOT.jar \
#     -agentpath:${CUR_DIR}/build/libagent.so=DataCentric::MEM_LOAD_UOPS_RETIRED:L1_MISS:precise=2@10000 -jar \
#     ${CUR_DIR}/dacapo.jar -s large lusearch

# cpucycles mode
LD_PRELOAD=$JXPerf_HOME/build/preload/libpreload.so
java \
    -agentpath:$JXPerf_HOME/build/libagent.so=Generic::CYCLES:precise=0@1000000 -jar \
    $JXPerf_HOME/benchmark/dacapo.jar -s large lusearch
    