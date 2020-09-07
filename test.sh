#! /bin/bash
CUR_DIR=$(cd "$(dirname "$0")";pwd)
JVMTI_AGENT="$CUR_DIR"/build/libagent.so=DataCentric::MEM_LOAD_UOPS_RETIRED:L1_MISS:precise=2@100000
BENCHMARK_DIR="$CUR_DIR"/benchmark/dacapo.jar
BENCHMARK=lusearch
JAVA=java
JAVAAGENT_OPTION=-javaagent:
JVMTIAGENT_OPTION=-agentpath:
JAR=-jar

export LD_PRELOAD="$CUR_DIR"/build/preload/libpreload.so
"$JAVA" "$JAVAAGENT_OPTION"$JAVA_AGENT "$JVMTIAGENT_OPTION""$JVMTI_AGENT" "$JAR" "$BENCHMARK_DIR" "$BENCHMARK"
