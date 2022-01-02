# 1.CPU Cycles
# LD_PRELOAD=$JXPerf_HOME/build/preload/libpreload.so
# java \
#     -agentpath:$JXPerf_HOME/build/libagent.so=Generic::CYCLES:precise=2@1000000 \
#     -jar ./dacapo.jar lusearch

# 2.Data-centric
LD_PRELOAD=$JXPerf_HOME/build/preload/libpreload.so
java -javaagent:$JXPerf_HOME/thirdparty/allocation-instrumenter/target/java-allocation-instrumenter-HEAD-SNAPSHOT.jar -agentpath:$JXPerf_HOME/build/libagent.so=DataCentric::MEM_LOAD_UOPS_RETIRED:L1_MISS:precise=2@10000 -jar ./dacapo.jar -s large lusearch

# 3.Heap usage
# LD_PRELOAD=$JXPerf_HOME/build/preload/libpreload.so
# java \
#     -agentpath:$JXPerf_HOME/build/libagent.so=Heap \
#     -jar ./dacapo.jar -s large lusearch
