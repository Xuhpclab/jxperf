#!/bin/bash

ATTACH=$JXPerf_HOME/bin/jattach/attach
MODE=DataCentric::MEM_LOAD_UOPS_RETIRED:L1_MISS:precise=2@1000000
PID="$1"
DURATION="$2"
ATTACH_TO_JAVA_AGENT=load instrument false $JXPerf_HOME/thirdparty/allocation-instrumenter/target/java-allocation-instrumenter-HEAD-SNAPSHOT.jar
ATTACH_TO_JVMTI_AGENT_START=load $JXPerf_HOME/build/libagent.so true
ATTACH_TO_JVMTI_AGENT_STOP=load $JXPerf_HOME/build/libstop.so true

"$ATTACH" "$PID" "$ATTACH_TO_JAVA_AGENT"
"$ATTACH" "$PID" "$ATTACH_TO_JVMTI_AGENT_START" "$MODE"s
while (( DURATION-- > 0 ))
do
    sleep 1
done
"$ATTACH" "$PID" "$ATTACH_TO_JVMTI_AGENT_STOP" "$MODE"p
