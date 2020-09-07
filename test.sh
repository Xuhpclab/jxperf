#! /bin/bash
CUR_DIR=$(cd "$(dirname "$0")";pwd)
JVMTI_AGENT="$CUR_DIR"/build/libagent.so=DataCentric::MEM_LOAD_UOPS_RETIRED:L1_MISS:precise=2@100000
BENCHMARK_DIR="$CUR_DIR"/benchmark/dacapo.jar
BENCHMARK=lusearch

export LD_PRELOAD="$CUR_DIR"/build/preload/libpreload.so
java -javaagent:$JAVA_AGENT -agentpath:"$JVMTI_AGENT" -jar "$BENCHMARK_DIR" "$BENCHMARK"
