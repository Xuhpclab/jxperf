# CPU Cycles
# LD_PRELOAD=$JXPerf_HOME/build/libpreload.so
# java \
#     -agentpath:$JXPerf_HOME/build/libagent.so=Generic::CYCLES:precise=2@100000 \
#     -jar ./dacapo.jar lusearch

# dead store
# LD_PRELOAD=$JXPerf_HOME/build/preload/libpreload.so
# java -agentpath:$JXPerf_HOME/build/libagent.so=SilentStore::MEM_UOPS_RETIRED:ALL_STORES:precise=2@100000 -jar ./dacapo.jar lusearch

# data centric
# LD_PRELOAD=$JXPerf_HOME/build/preload/libpreload.so
# java -javaagent:$JXPerf_HOME/thirdparty/allocation-instrumenter/target/java-allocation-instrumenter-HEAD-SNAPSHOT.jar -agentpath:$JXPerf_HOME/build/libagent.so=DataCentric::MEM_LOAD_UOPS_RETIRED:L1_MISS:precise=2@10000 -jar ./dacapo.jar -s large lusearch

# Heap usage
LD_PRELOAD=$JXPerf_HOME/build/preload/libpreload.so
java \
    -agentpath:$JXPerf_HOME/build/libagent.so=Heap \
    -jar ./dacapo.jar -s large lusearch

# Offline process -- VS Code GUI
# $JXPerf_HOME/script/process_raw_data_to_vscode.py $JXPerf_HOME/benchmark/lucene

# View
# code ./lucene
