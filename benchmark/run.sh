# CPU Cycles
# LD_PRELOAD=$JXPerf_HOME/build/preload/libpreload.so
# java \
#     -agentpath:$JXPerf_HOME/build/libagent.so=Generic::CYCLES:precise=2@100000 \
#     -jar ./dacapo.jar lusearch

# dead store
# LD_PRELOAD=$JXPerf_HOME/build/preload/libpreload.so
# java -agentpath:$JXPerf_HOME/build/libagent.so=SilentStore::MEM_UOPS_RETIRED:ALL_STORES:precise=2@100000 -jar ./dacapo.jar lusearch

# heap
# LD_PRELOAD=$JXPerf_HOME/build/preload/libpreload.so
# java \
#     -agentpath:$JXPerf_HOME/build/libagent.so=Heap \
#     -jar ./dacapo.jar lusearch
