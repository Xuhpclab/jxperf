# CPU Cycles
# LD_PRELOAD=$JXPerf_HOME/build/libpreload.so
# java \
#     -agentpath:$JXPerf_HOME/build/libagent.so=Generic::CYCLES:precise=2@100000 \
#     -jar ./dacapo.jar lusearch

# dead store
LD_PRELOAD=$JXPerf_HOME/build/preload/libpreload.so
java -agentpath:$JXPerf_HOME/build/libagent.so=SilentStore::MEM_UOPS_RETIRED:ALL_STORES:precise=2@100000 -jar ./dacapo.jar lusearch

# Offline process -- VS Code GUI
# $JXPerf_HOME/script/process_raw_data_to_vscode.py /home/bli35/jxperf/benchmark/lucene

# View
# code ./lucene
