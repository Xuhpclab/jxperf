#! /bin/bash
CUR_DIR=$(cd "$(dirname "$0")";pwd)

export LD_PRELOAD=${CUR_DIR}/build/preload/libpreload.so
java \
    -javaagent:$JAVA_AGENT \
    -agentpath:${CUR_DIR}/build/libagent.so=DataCentric::MEM_LOAD_UOPS_RETIRED:L1_MISS:precise=2@100000 -jar \
    ${CUR_DIR}/benchmark/dacapo.jar lusearch

#${CUR_DIR}/script/process_raw_data.py
